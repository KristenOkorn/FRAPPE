# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 12:13:46 2023

@author: okorn
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 12:13:46 2023
Using ANN with early stopping to model regulatory surface concentration
as a function of: pods, Pandoras, & model (still need to add model)
@author: okorn
"""


#Import helpful toolboxes etc
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import tensorflow
import seaborn as sns
import tensorflow
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.callbacks import EarlyStopping
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

        #Scale the input features (X) using StandardScaler
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
       
        #Define the EarlyStopping callback
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

        #Create a Sequential model
        model = Sequential()

        #Add input layer and hidden layers
        model.add(Dense(32, activation='relu', input_shape=(X_train_scaled.shape[1],)))
        model.add(Dense(16, activation='relu'))

        #Add output layer
        model.add(Dense(1))

        #Compile the model
        model.compile(optimizer=RMSprop(), loss='mean_squared_error')

        #Train the model on the training data
        model.fit(X_train_scaled, y_train, batch_size=32, epochs=100, verbose=1,callbacks=[early_stopping])
        
        # make predictions
        y_hat_train = model.predict(X_train_scaled)
        y_hat_test = model.predict(X_test_scaled)
        
        #Get the weights and biases of the final model
        weights = model.get_weights()

        #Create a DataFrame to store the weights and biases
        weights_df = pd.DataFrame(columns=['Variable', 'Weights', 'Biases'])

        #Iterate over the variables and their corresponding weights and biases
        for i, variable in enumerate(X_train.columns):
            weights_df = weights_df.append({'Variable': variable, 'Weights': weights[0][i], 'Biases': weights[1][i]}, ignore_index=True)

        #-------------------------------------------------------

        #perform a gradient-based sensitivity analysis to validate our results

        #Convert our input data to TensorFlow tensors
        X_tensor = tensorflow.constant(X_train.values)

        #Create a GradientTape context
        with tensorflow.GradientTape() as tape:
            #Watch the input tensor
            tape.watch(X_tensor)

            #Get the model predictions
            predictions = model(X_tensor)

        #Calculate the gradients of the predictions with respect to the input tensor
        input_gradients = tape.gradient(predictions, X_tensor)

        #Calculate the sensitivity scores based on the gradients
        sensitivity_scores = np.mean(np.abs(input_gradients.numpy()), axis=0)

        #Create a DataFrame with variable names and sensitivity scores
        sensitivity = pd.DataFrame({'Variable': X_train.columns, 'Sensitivity Score': sensitivity_scores})
        #-------------------------------------------------------

        #generate statistics for test data
        r2 = r2_score(y_test['ground_{}'.format(pollutants[n])], y_hat_test)
        rmse = np.sqrt(mean_squared_error(y_test['ground_{}'.format(pollutants[n])], y_hat_test))
        #Convert the Series to a NumPy array
        y_test_array = y_test.values
        mbe = np.mean(y_hat_test - y_test_array)
        #store our results in a dictionary
        stats_test = {'R2': r2, 'RMSE': rmse, 'MBE': mbe}
        
        #now add the predictions  & y's back to the original dataframes
        X_train['y_hat_train'] = y_hat_train
        X_test['y_hat_test'] = y_hat_test
        X_train['Y'] = y
        
        #generate statistics for train data
        r2 = r2_score(y_train['ground_{}'.format(pollutants[n])], y_hat_train)
        rmse = np.sqrt(mean_squared_error(y_train['ground_{}'.format(pollutants[n])], y_hat_train))
        #Convert the Series to a NumPy array
        y_train_array = y_train.values
        mbe = np.mean(y_hat_train - y_train_array)
        #store our results in a dictionary
        stats_train = {'R2': r2, 'RMSE': rmse, 'MBE': mbe}
        
        #save all of our results to file
        
        #Name a new subfolder
        subfolder_name = 'Outputs_{}_ann_earlystop_rms'.format(pollutants[n])
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
        
        #weights & biases
        savePath = os.path.join(subfolder_path,'{}_weights_bias_{}.csv'.format(locations[k],pollutants[n]))
        # Convert the dictionary to a DataFrame
        weights_df.to_csv(savePath)
        
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
        
        #sensitivity analysis
        savePath = os.path.join(subfolder_path,'{}_sensitivity_{}.csv'.format(locations[k],pollutants[n]))
        sensitivity.to_csv(savePath)