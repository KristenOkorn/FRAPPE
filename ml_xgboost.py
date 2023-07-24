# -*- coding: utf-8 -*-
"""
Created on Fri May 26 13:15:27 2023

**Tuning notes**
At max depth = 6, starts to overfit - leaving at 5 for now
Learning rate needs to be between 0 and 1 - leaving at 1 for now

Factor importance
NO2 - only 1/3 models weights pandora data the highest
O3 - 0/3 models weight pandora the highest (usually hour)
@author: okorn
"""
#Import helpful toolboxes etc
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

#list of pollutants to model
pollutants = ['O3','NO2']

#list of pods to model
pods = ['YPODD4','YPODD8', 'YPODN8']

#create a directory path for us to pull from / save to
path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\BAO\\Ground-Based Estimates\\'

for n in range(len(pollutants)):
    #load the ML input data
    filename = "BAO_inputs_{}.csv".format(pollutants[n])
    #combine the file and the path
    filepath = os.path.join(path, filename)
    ann_inputs = pd.read_csv(filepath,index_col=0)
    # Convert the index to a DatetimeIndex and set the nanosecond values to zero
    ann_inputs.index = pd.to_datetime(ann_inputs.index.values.astype('datetime64[s]'),format="%Y-%m-%d %H:%M:%S", errors='coerce')
    

    for k in range(len(pods)):
        #load the pod data
        filename = "{}_{}.csv".format(pods[k],pollutants[n])
        #combine the file and the path
        filepath = os.path.join(path, filename)
        pod = pd.read_csv(filepath,index_col=0)  
        # Convert Index to DatetimeIndex
        pod.index = pd.to_datetime(pod.index, format="%d-%b-%Y %H:%M:%S")
        #Convert the modified index to a DatetimeIndex and set the nanosecond values to zero
        pod.index = pd.to_datetime(pod.index.values.astype('datetime64[s]'), errors='coerce')
   
        #combine our datasets - both already in local time
        x=pd.merge(ann_inputs,pod,left_index=True,right_index=True)
        
        #Remove whitespace from column labels
        x.columns = x.columns.str.strip()
        
        #now for reformatting - get our 'y' data alone
        y = pd.DataFrame(x.pop('{}'.format(pollutants[n])))
        
        #Now do our test-train split
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=.2)

        #create model instance
        bst = XGBRegressor(objective='reg:squarederror', n_estimators=len(x.columns), max_depth=5, learning_rate=1)
        
        #fit the model
        bst.fit(X_train, y_train)
        
        # make predictions
        y_hat_train = bst.predict(X_train)
        y_hat_test = bst.predict(X_test)
        
        #now add the predictions  & y's back to the original dataframes
        X_train['y_hat_train'] = y_hat_train
        X_test['y_hat_test'] = y_hat_test
        X_train['Y'] = y
        
        #Get the feature importances
        importances = bst.feature_importances_
        
        #Create a dictionary of importance labels with their corresponding input labels
        importance_labels = {label: importance for label, importance in zip(x.columns, importances)}
        
        #generate statistics for test data
        r2 = r2_score(y_test['{}'.format(pollutants[n])], y_hat_test)
        rmse = np.sqrt(mean_squared_error(y_test['{}'.format(pollutants[n])], y_hat_test))
        mbe = np.mean(y_hat_test - y_test['{}'.format(pollutants[n])])
        #store our results in a dictionary
        stats_test = {'R2': r2, 'RMSE': rmse, 'MBE': mbe}
        
        #generate statistics for train data
        r2 = r2_score(y_train['{}'.format(pollutants[n])], y_hat_train)
        rmse = np.sqrt(mean_squared_error(y_train['{}'.format(pollutants[n])], y_hat_train))
        mbe = np.mean(y_hat_train - y_train['{}'.format(pollutants[n])])
        #store our results in a dictionary
        stats_train = {'R2': r2, 'RMSE': rmse, 'MBE': mbe}
        
        #save all of our results to file
        
        #Name a new subfolder
        subfolder_name = 'Outputs_{}_xgboost'.format(pollutants[n])
        #Create the subfolder path
        subfolder_path = os.path.join(path, subfolder_name)
        #Create the subfolder
        os.makedirs(subfolder_path, exist_ok=True)

        #save out the final data
        
        #X_train
        savePath = os.path.join(subfolder_path,'{}_X_train_{}.csv'.format(pods[k],pollutants[n]))
        X_train.to_csv(savePath)
        
        #X_test
        savePath = os.path.join(subfolder_path,'{}_X_test_{}.csv'.format(pods[k],pollutants[n]))
        X_test.to_csv(savePath)
        
        #Importance labels
        savePath = os.path.join(subfolder_path,'{}_Factor_importance_{}.csv'.format(pods[k],pollutants[n]))
        # Convert the dictionary to a DataFrame
        importance_labels = pd.DataFrame.from_dict(importance_labels, orient='index', columns=['Value'])
        importance_labels.to_csv(savePath)
        
        #Stats_train
        savePath = os.path.join(subfolder_path,'{}_stats_train_{}.csv'.format(pods[k],pollutants[n]))
        # Convert the dictionary to a DataFrame
        stats_train = pd.DataFrame.from_dict(stats_train, orient='index', columns=['Value'])
        stats_train.to_csv(savePath)
        
        #Stats_test
        savePath = os.path.join(subfolder_path,'{}_stats_test_{}.csv'.format(pods[k],pollutants[n]))
        # Convert the dictionary to a DataFrame
        stats_test = pd.DataFrame.from_dict(stats_test, orient='index', columns=['Value'])
        stats_test.to_csv(savePath)