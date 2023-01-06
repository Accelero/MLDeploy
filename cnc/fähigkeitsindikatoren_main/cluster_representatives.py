import numpy as np
import pandas as pd
import torch.nn as nn
import torch


def rep_features(lables, features):
    # Calculate representative features for inline identification
    class_nrs = np.unique(lables).tolist()

    if class_nrs.__contains__(-1):
        class_nrs.remove(-1)

    class_features = []
    class_std = []

    for class_nr in class_nrs:

        # Calculate class features
        class_index = np.where(lables == class_nr)[0].tolist()
        raw_class_feature = features[class_index]

        # Calculate the mean Features
        class_features += [raw_class_feature.mean(axis=0).tolist()]

        # Calculate the std for the features of an class
        class_std += [raw_class_feature.std(axis=0).tolist()]

    return class_features, class_std

def get_cluster_ts(data, lables):
    # Get all timeseries for the representation of an clusters in correct order: cluster --> source --> all ts
    # for each class the first "nr_ts" will be collected

    # Get all class lables
    class_nrs = np.unique(lables).tolist()

    if class_nrs.__contains__(-1):
        class_nrs.remove(-1)

    # Get the timeseries data
    raw_ts = [np.array(single_data[3]) for single_data in data]
    count_ts = len(raw_ts[0][0])

    class_rep = []   # List for representative class ts
    class_len_rep = []   # List for representative len of an class

    for class_nr in class_nrs:
        nr_ts = 3   # Nr of the first ts of an class, wich will be considered
        class_index = np.where(lables == [class_nr])[0]
        class_index_short = class_index[:nr_ts]

        # get the lenth data of an class considereing all class ts
        class_len = [ len(raw_ts[index]) for index in class_index]
        class_len_data = [min(class_len), max(class_len)]
        class_len_rep += [class_len_data[0]]

        # Get the represnetative ts and add them to the class_rep list
        rep_ts = []
        for i in range(count_ts):
            rep_ts += [[ raw_ts[index][:class_len_data[0], i].tolist() for index in class_index_short]]

        class_rep += [rep_ts]

    return class_rep, class_len_rep


def reference_series_old(Data):
    # Calculates the reference series and the upper/lower thresholds for the representative class data (old version)

    df = pd.DataFrame(Data).T

    f_samp = 500   # Sampleing frequence
    std_factor = 6   # Factor for std
    len1 = int(f_samp/10) # window size for rolling mean/std
    len2 = int(f_samp/25) # std size for gaussian filter

    # Calculate rolling mean and rolling std for every series
    df_mean = df.rolling(len1, win_type = 'gaussian', center = True).mean(std = len2)
    df_std = df.rolling(len1, win_type = 'gaussian', center = True).std(std = len2)*std_factor

    # Normalize df_std useing the deviation of the mean
    df_std = df_std/(1+(std_factor/3)*df_mean.rolling(len1, win_type = 'gaussian',center=True).std(std = len2))

    # Smooth df_std useing a rooling mean
    df_std = df_std.rolling(len1, win_type = 'gaussian', center = True).mean(std=len2)

    # Caldulate the mean betweeen all series
    std = df_std.T.mean()
    mean = df_mean.T.mean().tolist()

    # Calculate upper and lower threshold
    max_ = (mean+std).rolling(len1,center = True).max().tolist()
    min_ = (mean-std).rolling(len1,center = True).min().tolist()

    return mean, max_, min_

def reference_series(Data):
    # Calculates the reference series and the upper/lower thresholds for the representative class data

    f_samp = 500   # Sampleing frequence
    std_factor = 6   # Factor for std
    len1= int(f_samp/10) # window size for rolling mean/std
    len2= int(f_samp/20) # std size for gaussian filter
    median = []
    min_ = []
    max_ = []

    # Calculate median and upper/lower threshold for a given neighborhood of all reference series
    for i in range(len(Data[0])-len1):

        neighborhood = np.array([Data[ii][i:i+len1] for ii in range(len(Data))])
        median_n = np.median(neighborhood)

        # calculate the percentiles
        p_80 = np.percentile(neighborhood, 80)
        p_20 = np.percentile(neighborhood, 20)

        std_n = np.std(neighborhood)
        median += [median_n]
        min_ += [median_n-std_n*std_factor/(1+abs(p_80-p_20))**2]
        max_ += [median_n+std_n*std_factor/(1+abs(p_80-p_20))**2]

    # median and upper/lower threshold
    max_=(pd.Series(max_)).rolling(len2,center=True).mean().dropna().tolist()
    min_=(pd.Series(min_)).rolling(len2,center=True).mean().dropna().tolist()
    median=(pd.Series(median)).rolling(len2,center=True).mean().dropna().tolist()

    # Use first/last entrie to fill Series to original length
    diff = len1 + len2 - 1
    median = [median[0]]*int(diff/2) + median + [median[-1]]*(diff-int(diff/2))
    min_ = [min_[0]]*int(diff/2) + min_ + [min_[-1]]*(diff-int(diff/2))
    max_ = [max_[0]]*int(diff/2) + max_ + [max_[-1]]*(diff-int(diff/2))

    return median, max_, min_


class Autoencoder(nn.Module):
    # Autoencoder class for the calculation of reconstucion errors
    def __init__(self, class_len_rep):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(class_len_rep, 128),
            nn.ReLU(),
            nn.Linear(128, 32),
            nn.ReLU(),
            nn.Linear(32, 8),
        )

        self.decoder = nn.Sequential(
            nn.Linear(8, 32),
            nn.ReLU(),
            nn.Linear(32, 128),
            nn.ReLU(),
            nn.Linear(128, class_len_rep)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded



class signal_index():
    # signal index class containing all representative informations if a signal

    def __init__(self, rep_data, class_len_rep):
        self.CLASS_LEN_REP = class_len_rep
        self.MEDIAN, self.MAX_, self.MIN_ = reference_series(rep_data)
        self.GLOBAL_MEAN = sum(np.absolute(self.MEDIAN))/len(self.MEDIAN)
        self.MODEL = self._train_autoencoder(rep_data)


    def _train_autoencoder(self, rep_data):
        # train the Autoencoder useing the representative timeseries for a Signal

        train = torch.tensor(rep_data, dtype = torch.float32)
        data_loader = torch.utils.data.DataLoader(dataset=train, batch_size=16, shuffle=True)

        model = Autoencoder(self.CLASS_LEN_REP)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=0)

        num_epochs = 100   # Training epochs
        outputs = []
        for epoch in range(num_epochs):
            for input in data_loader:
                recon = model(input)
                loss = criterion(recon, input)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # print(f'Epoch:{epoch+1}, Loss:{loss.item(): .4f}')
            # outputs.append((epoch, input, recon))

        return model

    def get_index(self, data, type = 'mean'):
        # get the curent value of an index based on the selected metric

        if type == 'rec_error':
            # reconsturction error as index
            error = torch.tensor(pd.Series(data), dtype=torch.float32)
            index = sum(self.MODEL.forward(error)-error).item()/self.CLASS_LEN_REP

        if type == 'dist_to_mean':
            # distance as index
            index =  sum([abs(data[ii]-self.MEDIAN[ii])/self.CLASS_LEN_REP for ii in range(len(data))])
        if type == 'mean':
            # distance between abs of global mean is index
            index = self.GLOBAL_MEAN - sum(np.absolute(data))/len(data)

        return index

def get_cluster_ts(data, lables):
    # Get all timeseries for the representation of an clusters in correct order: cluster --> source --> all ts
    # for each class the first "nr_ts" will be collected

    # Get all class lables
    class_nrs = np.unique(lables).tolist()

    if class_nrs.__contains__(-1):
        class_nrs.remove(-1)

    # Get the timeseries data
    raw_ts = [np.array(single_data[3]) for single_data in data]
    count_ts = len(raw_ts[0][0])

    class_rep = []   # List for representative class ts
    class_len_rep = []   # List for representative len of an class

    for class_nr in class_nrs:
        nr_ts = 3   # Nr of the first ts of an class, wich will be considered
        class_index = np.where(lables == [class_nr])[0]
        class_index_short = class_index[:nr_ts]

        # get the lenth data of an class considereing all class ts
        class_len = [ len(raw_ts[index]) for index in class_index]
        class_len_data = [min(class_len), max(class_len)]
        class_len_rep += [class_len_data[0]]

        # Get the represnetative ts and add them to the class_rep list
        rep_ts = []
        for i in range(count_ts):
            rep_ts += [[ raw_ts[index][:class_len_data[0], i].tolist() for index in class_index_short]]

        class_rep += [rep_ts]

    return class_rep, class_len_rep


def get_cluster_ts_inline(data, lables):
    # Get all timeseries for the clusters in correct order: cluster --> source --> Timeseries

    # Get all class lables
    class_nrs = np.unique(lables).tolist()

    if class_nrs.__contains__(-1):
        class_nrs.remove(-1)

    # Get the timeseries data
    raw_ts = [np.array(single_data[3]) for single_data in data]
    count_ts = len(raw_ts[0][0])

    class_rep = []   # List for class ts
    class_len_rep = []   # List for representative len of an class

    for class_nr in class_nrs:
        class_index = np.where(lables == [class_nr])[0]
        class_index_short = class_index[:]

        # get the lenth data of an class considereing all class ts
        class_len = [ len(raw_ts[index]) for index in class_index]
        class_len_data = [min(class_len), max(class_len)]

        # Get the represnetative ts and add them to the class_rep list
        rep_ts = []
        for i in range(count_ts):
            rep_ts += [[ raw_ts[index][:class_len_data[0],i].tolist() for index in class_index_short]]

        class_rep += [rep_ts]
        class_len_rep += [class_len_data[0]]

    return class_rep, class_len_rep, class_nrs


