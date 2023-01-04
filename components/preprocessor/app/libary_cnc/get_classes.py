from sklearn.cluster import DBSCAN
from sklearn import preprocessing
import numpy as np

def init_class(features):
    # Claculate the initial class useing DBCSCAN and return the lables (-1 = noise)
    clustering = DBSCAN(eps=1, min_samples=3).fit(features)

    return clustering.labels_

def normalization(features):
    # normalize a veature vector

    return preprocessing.normalize(features, axis=0, return_norm = True)

def inline_class(features, class_features, class_std):
    # Calculate the inline Class
    class_list = []
    
    for i_feature in features.tolist():
        found = False
        for i_rep in range(len(class_features)):
            # assign the class if all features are closer than 6*std
            if all([abs(class_features[i_rep][i]-i_feature[i]) <= 6*class_std[i_rep][i] for i in range(len(class_features[i_rep]))]):
                class_list += [i_rep]
                found = True

        if not found:
            # Assign -1 ifor all unasignd classes
            class_list += [-1]
    
    return np.array(class_list)