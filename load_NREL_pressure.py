# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 09:09:19 2024

Load in the NREL pressure / met data

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

#save out the final data
savePath = os.path.join(path,'Pressure_NREL.csv')
met.to_csv(savePath)