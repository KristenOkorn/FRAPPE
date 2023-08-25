# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 12:23:07 2023
Using xgboost to model regulatory surface concentration
as a function of: pods, Pandoras, & model (still need to add model)
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

#locations
locations = ['BAO','Platteville']

#loop through for each pollutant
for n in range(len(pollutants)):
    
    for k in range(len(locations)):
    
        #create a directory path for us to pull from / save to
        path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\Estimating Ground\\{}\\{}'.format(pollutants[n],locations[k])

        #Get the list of files from this directory
        from os import listdir
        from os.path import isfile, join
        fileList = [f for f in listdir(path) if isfile(join(path, f))]
    
        #iterate over each file in the main folder
        for i in range(len(fileList)):
            
            #get the pod name by itself
            podName = fileList[i][:6]
            
            #Create full file path for reading file
            filePath = os.path.join(path, fileList[i])
            
            #load in the file (if it's not the ml inputs)
            if podName != 'inputs':
        
                #load it in
                pod = pd.read_csv(filePath)
        
                #------Get concentration data------
                #if ozone, convert to ppb for pods
                #regulatory already in ppb
                if pollutants[n] == 'O3' and 'YPOD' in fileList[i]:
                    pod['O3'] = pod['O3'] * 1000
        
                #remove any whitespaces (may be causing our issue)
                pod.columns = pod.columns.str.strip()
                
                #rename the observed values
                pod = pod.rename(columns= {'{}'.format(pollutants[n]) : '{}_{}'.format(podName,pollutants[n])})
        
                #Convert the index to a DatetimeIndex and set the nanosecond values to zero
                pod.index = pd.to_datetime(pod['datetime'],errors='coerce')
    
                #drop the original datetime column
                pod = pod.drop(columns=['datetime'])
    
                #resample to hourly
                pod = pod.resample('H').mean()
        
                #remove negatives
                pod = pod[pod.iloc[:, 0] >= 0]
        
                #if this is the first iteration, make our dataframe the first
                if i == 0:
                    data = pod
                    #otherwise merge it with the existing ones
                else:
                    data = data.merge(pod, on='datetime', how='outer')
    
            #load the ML input data
            else:
                ann_inputs = pd.read_csv(filePath,index_col=0)
                #Convert the index to a DatetimeIndex and set the nanosecond values to zero
                ann_inputs.index = pd.to_datetime(ann_inputs.index.values.astype('datetime64[s]'),format="%Y-%m-%d %H:%M:%S", errors='coerce')
    
        #combine our datasets - both already in local time
        x=pd.merge(ann_inputs,data,left_index=True,right_index=True)
        
        #Remove whitespace from column labels
        x.columns = x.columns.str.strip()
        
        #remove nans (can't use rf regressor w nans)
        x = x.dropna(axis=0)
        
        #now for reformatting - get our 'y' data alone
        y = pd.DataFrame(x.pop('ground_{}'.format(pollutants[n])))
        
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
        r2 = r2_score(y_test['ground_{}'.format(pollutants[n])], y_hat_test)
        rmse = np.sqrt(mean_squared_error(y_test['ground_{}'.format(pollutants[n])], y_hat_test))
        mbe = np.mean(y_hat_test - y_test['ground_{}'.format(pollutants[n])])
        #store our results in a dictionary
        stats_test = {'R2': r2, 'RMSE': rmse, 'MBE': mbe}
        
        #generate statistics for train data
        r2 = r2_score(y_train['ground_{}'.format(pollutants[n])], y_hat_train)
        rmse = np.sqrt(mean_squared_error(y_train['ground_{}'.format(pollutants[n])], y_hat_train))
        mbe = np.mean(y_hat_train - y_train['ground_{}'.format(pollutants[n])])
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
        savePath = os.path.join(subfolder_path,'{}_X_train_{}.csv'.format(locations[k],pollutants[n]))
        X_train.to_csv(savePath)
        
        #X_test
        savePath = os.path.join(subfolder_path,'{}_X_test_{}.csv'.format(locations[k],pollutants[n]))
        X_test.to_csv(savePath)
        
        #Importance labels
        savePath = os.path.join(subfolder_path,'{}_Factor_importance_{}.csv'.format(locations[k],pollutants[n]))
        # Convert the dictionary to a DataFrame
        importance_labels = pd.DataFrame.from_dict(importance_labels, orient='index', columns=['Value'])
        importance_labels.to_csv(savePath)
        
        #Stats_train
        savePath = os.path.join(subfolder_path,'{}_stats_train_{}.csv'.format(locations[k],pollutants[n]))
        # Convert the dictionary to a DataFrame
        stats_train = pd.DataFrame.from_dict(stats_train, orient='index', columns=['Value'])
        stats_train.to_csv(savePath)
        
        #Stats_test
        savePath = os.path.join(subfolder_path,'{}_stats_test_{}.csv'.format(locations[k],pollutants[n]))
        # Convert the dictionary to a DataFrame
        stats_test = pd.DataFrame.from_dict(stats_test, orient='index', columns=['Value'])
        stats_test.to_csv(savePath)