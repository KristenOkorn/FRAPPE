# -*- coding: utf-8 -*-
"""
Created on Mon May  1 16:45:57 2023

Get the Pandora, wind, and time of day data in one table to use for ML
(BAO site only)

@author: okorn
"""

#Import helpful toolboxes etc
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta

#create a directory path for us to pull from / save to
path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\NREL\\'

#pollutant loop first

#set up pollutant structures to loop through
pollutants = ['O3','NO2']

#load in the met data
#Create full file path for reading file
filePath = os.path.join(path,'MET.ict')
#load in the file
met = pd.read_csv(filePath,skiprows=52)
#correct the day of year column format
met[' start_DOY-UTC']=met[' start_DOY-UTC'].astype(int)
# Create a datetime object using the year and day of year
met['datetime'] = [datetime(2014, 1, 1) + timedelta(t - 1) for t in met[' start_DOY-UTC']]
#now add the seconds
met['datetime'] += pd.to_timedelta(met[' start_sec-UTC'], unit='s')
#only keep the columns we really need
met = met.loc[:, ['datetime',' BPress_mbar ']]
#make the datetime the index
met.index = pd.to_datetime(met['datetime'],errors='coerce')
#get rid of the original datetime column
met = met.drop('datetime',axis=1)

# Set the datetime index back by 6 hours  (MDT)
met.index = met.index - pd.Timedelta(hours=6)

met = met.rename(columns={' BPress_mbar ' : 'Pressure'})

#loop through for each pollutant
for n in range(len(pollutants)):

    #set up location structures to loop through
    locations = ['NREL']

    #loop through for each location
    for i in range(len(locations)):
        
        #load in the pandora data
        filename = "Pandora_{}_{}.csv".format(locations[i],pollutants[n])
        # read in the first worksheet from the workbook myexcel.xlsx
        filepath = os.path.join(path, filename)
        pandora = pd.read_csv(filepath,index_col=0)
        pandora = pandora.drop(columns=['Temp-Eff'])
        pandora.index.names = ['datetime']
        pandora.columns.values[0] = 'pandora'
        # Convert the index to a DatetimeIndex and set the nanosecond values to zero
        pandora.index = pd.to_datetime(pandora.index,errors='coerce')
        
        # Set the datetime index back by 6 hours  (MDT)
        pandora.index = pandora.index - pd.Timedelta(hours=6)
                
        #Merge the data based on datetime index
        merge=pd.merge(pandora,met,left_index=True,right_index=True)
        
        #get the hour of day (to use as a variable)
        merge['hour'] = [t.hour for t in merge.index]
        
        #save out the final data
        savePath = os.path.join(path,'NREL_inputs_{}.csv'.format(pollutants[n]))
        merge.to_csv(savePath)