import matplotlib.pyplot as plt
import numpy as np
from libary_cnc import load_data
from libary_cnc import Zuschneiden
from libary_cnc import Features
from libary_cnc import get_classes
from libary_cnc import cluster_representatives
import pickle

# load Data
with open('data/class_features.pkl', 'rb') as class_features_file:
    class_features = pickle.load(class_features_file)

with open('data/class_std.pkl', 'rb') as class_std_file_file:
    class_std = pickle.load(class_std_file_file)

with open('data/class_index_models.pkl', 'rb') as class_index_models_file:
    class_index_models = pickle.load(class_index_models_file)

with open('data/index_matrix.pkl', 'rb') as index_matrix_file:
    index_matrix = pickle.load(index_matrix_file)


#############
# load initial data and calculate sequences
matrix,static_features,kopfzeile=load_data.load_matrix(r"./CSV_SDMflex/SDMflex_V2_Anwendung_final.csv")   # load learning Data
Schnitt = Zuschneiden.Sectioning(matrix,kopfzeile,G=1, c=True)   # calculate sequences
Zuschnitte = Features.region_feature(matrix,Schnitt,kopfzeile,static_features)   # calculate features

#############
# get feature vector for segmentation
features=[]
for i in range(len(Zuschnitte)):
    # Used features are distance (x,y,z), average spindle speed and duration (spindlespeed is diveded by 6 due to recording)
    features += [(Zuschnitte[i][1][0], Zuschnitte[i][1][1],Zuschnitte[i][1][2], Zuschnitte[i][1][4]/6, Zuschnitte[i][1][5])]
features = np.array(features)

# inline segmentation
inline_lables = get_classes.inline_class(features, class_features, class_std)

#############
# Calculation of the values for each Sequence and addit to the index_matrix
class_rep, class_len_rep, class_nrs_inline = cluster_representatives.get_cluster_ts_inline(Zuschnitte, inline_lables)  # get the sorted representative cluster timeseries (cluster --> source --> all ts)

print(len(index_matrix))
index = np.linspace(kopfzeile.index('Speed_SP')+1, len(kopfzeile)-1, len(kopfzeile) - kopfzeile.index('Speed_SP') - 1).astype(int)   # get relevant indices

# Update the index-matrix based on the current metric
for i in range(len(class_nrs_inline)):
    class_nr = class_nrs_inline[i]

    for sig_index in index:
        for nr_ts in range(len(class_rep[i][sig_index])):

            index_matrix[class_nr][sig_index - kopfzeile.index('Speed_SP') - 1] += [class_index_models[class_nr][sig_index  - kopfzeile.index('Speed_SP') - 1].get_index(class_rep[i][sig_index][nr_ts], 'dist_to_mean')]