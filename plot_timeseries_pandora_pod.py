# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 15:43:30 2023

@author: okorn
"""

#Import helpful toolboxes etc
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.dates as mdates

#create a directory path for us to pull from / save to
path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\Pandora\\'

#pollutant loop first

#set up pollutant structures to loop through
pollutants = ['O3','NO2']

#loop through for each pollutant
for n in range(len(pollutants)):

    #set up location structures to loop through
    locations = ['BAO','NREL','Platteville']
    #loop through for each location
    for i in range(len(locations)):
        
        #plotting to initialize
        plt.xlabel("Datetime")
        #add string + variable for y axis
        y = '{}'.format(pollutants[n])
        plt.ylabel(y)
        #add string + variable for plot title
        titl = '{} {}'.format(locations[i],pollutants[n])
        plt.xticks(rotation = 45)
        plt.title(titl)
        
        #load in the pandora data
        filename = "Pandora_{}_{}.csv".format(locations[i],pollutants[n])
        # read in the first worksheet from the workbook myexcel.xlsx
        filepath = os.path.join(path, filename)
        pandora = pd.read_csv(filepath)  
        #reformat x data
        pandora['Date-GMT'] = pd.to_datetime(pandora['Date-GMT'], format='%Y-%m-%d %H:%M:%S')
        x = mdates.date2num(pandora['Date-GMT'])
        #reformat y to get on the same scale as pod data
        if n == 0:
            #e-20 for ozone
            pandora.iloc[:,1] = pandora.iloc[:,1] * 1e-20
            #plot
            plt.plot(x,pandora['{}'.format(pollutants[n])], label = 'Pandora e-20')
        else:
            #e-22 for NO2
            pandora.iloc[:,1] = pandora.iloc[:,1] * 1e-15
            #plot
            plt.plot(x,pandora['{}'.format(pollutants[n])], label = 'Pandora e-15')
        
        #get the pod names matching each location
        if locations[i] == 'BAO':
            pods = ['YPODD4']
        elif locations[i] == 'NREL':
            pods = ['YPODF1']
        else:
            pods = ['YPODF4','YPODF9']
        
        #load in the matching pod data
        for k in range(len(pods)):
            filename = "{}_{}.csv".format(pods[k],pollutants[n])
            # read in the first worksheet from the workbook myexcel.xlsx
            filepath = os.path.join(path, filename)
            pod = pd.read_csv(filepath)  
            # remove negatives
            pod = pod[pod.iloc[:, 1] >= 0]
            #reformat x data
            pod['datetime'] = pd.to_datetime(pod['datetime'], format="%m/%d/%Y %H:%M")
            x = mdates.date2num(pod['datetime'])
            #plot
            plt.plot(x,pod['{}'.format(pollutants[n])], label = '{}'.format(pods[k]))
            
        #reformat x data
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        #add a legend at the end
        plt.legend()

        #final plotting & saving
        imgname = '{}_{}_timeseries.png'.format(locations[i],pollutants[n])
        imgpath = os.path.join(path, imgname)
        plt.savefig(imgpath)
        plt.show()