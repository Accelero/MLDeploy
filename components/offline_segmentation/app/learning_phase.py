import numpy as np
from libary_cnc import load_data
from libary_cnc import Zuschneiden
from libary_cnc import Features
from libary_cnc import get_classes
from libary_cnc import cluster_representatives
import pickle
import pandas as pd

def start_learning():

    #############
    # load initial data and calculate sequences
    matrix,static_features,kopfzeile=load_data.load_matrix(r"./CSV_SDMflex/SDMflex_V2_Training_final.csv")   # load learning Data
    Schnitt = Zuschneiden.Sectioning(matrix,kopfzeile,G=1, c=True)   # calculate sequences
    Zuschnitte = Features.region_feature(matrix,Schnitt,kopfzeile,static_features)   # calculate features


    #############
    # get feature vector for segmentation
    features=[]
    for i in range(len(Zuschnitte)):
        # Used features are distance (x,y,z), average spindle speed and duration (spindlespeed is diveded by 6 due to recording)
        features += [(Zuschnitte[i][1][0], Zuschnitte[i][1][1],Zuschnitte[i][1][2], Zuschnitte[i][1][4]/6, Zuschnitte[i][1][5])]
    features = np.array(features)

    # Initial Segmentation
    lables = get_classes.init_class(features)


    #############
    # Calculate and save the representative cluster features for inline classification
    class_features, class_std = cluster_representatives.rep_features(lables, features)

    # with open('data/class_features.pkl', 'wb') as f:
    #     pickle.dump(class_features, f)

    # with open('data/class_std.pkl', 'wb') as f:
    #     pickle.dump(class_std, f)



    #############
    # Fill model matrix with models
    class_rep, class_len_rep = cluster_representatives.get_cluster_ts(Zuschnitte, lables)   # get the sorted representative cluster timeseries (cluster --> source --> all ts)

    index = np.linspace(kopfzeile.index('Speed_SP')+1, len(kopfzeile)-1, len(kopfzeile) - kopfzeile.index('Speed_SP')-1).astype(int)   # get relevant indices

    # Get the relevant lables (-1 --> noise)
    class_nrs = np.unique(lables).tolist()

    if class_nrs.__contains__(-1):
        class_nrs.remove(-1)

    class_index_models = []   # Matrix for the representative models
    index_matrix = []   #   frame-matrix for indices

    for class_nr in class_nrs:
        # check each cluster
        class_index = []
        class_index_vector = []

        for i in index:
            # get the signal-index model for each information signal
            class_index += [cluster_representatives.signal_index(class_rep[class_nr][i], class_len_rep[class_nr])]
            class_index_vector += [[]]

        class_index_models += [class_index]
        index_matrix += [class_index_vector]


    # with open('data/index_matrix.pkl', 'wb') as f:
    #     pickle.dump(index_matrix, f)

    # with open('data/class_index_models.pkl', 'wb') as f:
    #     pickle.dump(class_index_models, f)

    ret_dict = {
        'class_features' : class_features,
        'class_std' : class_std,
        'index_matrix' : index_matrix,
        'class_index_models' : class_index_models,

    }
    data = pd.DataFrame.from_dict(ret_dict)
    print(data)
    print ('finished learning_phase')

    return data