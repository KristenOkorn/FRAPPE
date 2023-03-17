# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 13:12:04 2023

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
        
        #load in the pandora data
        filename = "Pandora_{}_{}.csv".format(locations[i],pollutants[n])
        # read in the first worksheet from the workbook myexcel.xlsx
        filepath = os.path.join(path, filename)
        pandora = pd.read_csv(filepath)  
        #reformat x data
        pandora['Date-GMT'] = pd.to_datetime(pandora['Date-GMT'], format='%Y-%m-%d %H:%M:%S')
        x = mdates.date2num(pandora['Date-GMT'])
 
        # create figure and axes objects
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # create first axis with line plot
        ax1.plot(x,pandora['{}'.format(pollutants[n])], color='lightblue')
        ax1.set_ylabel('Pandora {} (molec/cm2)'.format(pollutants[n]), color='lightblue')
        ax1.tick_params(axis='y', labelcolor='lightblue')

            
        #get the pod names matching each location
        if locations[i] == 'BAO':
            pods = ['YPODD4']
        elif locations[i] == 'NREL':
            pods = ['YPODF1']
        else:
            pods = ['YPODF4']
        
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
            if pollutants[n] == 'O3':
                
                ax2 = ax1.twinx()
                ax2.plot(x,pod['{}'.format(pollutants[n])],color='orange')
                ax2.set_ylabel('INSTEP O3 (ppm)', color='orange')
                ax2.tick_params(axis='y', labelcolor='orange')
            else:
                ax2 = ax1.twinx()
                ax2.plot(x,pod['{}'.format(pollutants[n])],color='orange')
                ax2.set_ylabel('INSTEP NO2 (ppb)', color='orange')
                ax2.tick_params(axis='y', labelcolor='orange')
        
        #reformat x data
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # set x-axis label and title
        ax1.set_xlabel('Date')
        ax1.set_title('{} {}'.format(locations[i],pollutants[n]))

        #final plotting & saving
        imgname = '{}_{}_timeseries.png'.format(locations[i],pollutants[n])
        imgpath = os.path.join(path, imgname)
        plt.savefig(imgpath)
        plt.show()