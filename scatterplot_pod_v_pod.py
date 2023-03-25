
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 13:22:55 2023

Scatterplot of Pod vs. Pod

@author: okorn
"""

#Import helpful toolboxes etc
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

#create a directory path for us to pull from / save to
path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\Pods\\'

#set up pollutant structures to loop through
pollutants = ['O3','NO2','HCHO']
#also get the units for each
units = ['ppm','ppb','ppb']

#set up location structures to loop through
pods = ['YPODD4','YPODD6','YPODD8','YPODF1','YPODF3','YPODF7','YPODF8','YPODF9','YPODN4','YPODN5','YPODN7','YPODN8']
colors = ['red', 'green', 'blue', 'orange', 'purple', 'pink', 'brown', 'gray','m','k','aquamarine','mediumseagreen']

#loop through for each pollutant
for n in range(len(pollutants)):
    
    # create the subplots before the loop starts
    fig, axs = plt.subplots(3, 4, figsize=(20, 10))
    fig.subplots_adjust(wspace=0.3, hspace=0.5)
    
    #load in the main pod data
    filename = "YPODF4_{}.csv".format(pollutants[n])
    # read in the first worksheet from the workbook myexcel.xlsx
    filepath = os.path.join(path, filename)
    main_pod = pd.read_csv(filepath,index_col=0)
    main_pod.index.names = ['datetime']
    main_pod.columns.values[0] = 'pod_main'
    # Convert the index to a DatetimeIndex and set the nanosecond values to zero
    main_pod.index = pd.to_datetime(main_pod.index,errors='coerce')
            
    # Convert the date column to a datetime object if needed
    main_pod['date'] = pd.to_datetime(main_pod.index)
    # Get the list of unique days in the date column
    unique_days = pd.to_datetime(main_pod['date'].dt.date.unique())
    # Convert unique_days to datetime64[D] type
    unique_days = np.array(unique_days, dtype='datetime64[D]') 
        
    #now get the data for each location   
    for i in range(len(pods)):
        row = i // 4  # Integer division to get the row index
        col = i % 4  # Modulus operator to get the column index
        
        #now get the comparative data from the other pandoras
        filename = "{}_{}.csv".format(pods[i],pollutants[n])
        # read in the first worksheet from the workbook myexcel.xlsx
        filepath = os.path.join(path, filename)
        pod = pd.read_csv(filepath,index_col=0)
        pod.index.names = ['datetime']
        pod.columns.values[0] = 'pod'
        # Convert the index to a DatetimeIndex and set the nanosecond values to zero
        pod.index = pd.to_datetime(pod.index,errors='coerce')
    
        #Merge the data from both pandoras
        merge=pd.merge(main_pod,pod,left_index=True,right_index=True)
                
        axs[row,col].scatter(merge['pod_main'], merge['pod'],c=colors[i],alpha=0.5)
            
        #add trendline
        if not merge.empty:
            z = np.polyfit(merge['pod_main'], merge['pod'], 1) #calculate equation for trendline
            p = np.poly1d(z) #calculate points
            axs[row,col].plot(merge['pod_main'], p(merge['pod_main']),c=colors[i]) #add trendline to plot
    
        #add string + variable for plot title
        titl = '{} {}'.format(pods[i],pollutants[n])
        axs[row,col].set_title(titl)
        
        #add x & y axis labels
        x = 'YPODF4 {} ({})'.format(pollutants[n],units[n])
        axs[row,col].set_xlabel(x)
        y = '{} {} ({})'.format(pods[i],pollutants[n],units[n])
        axs[row,col].set_ylabel(y)  
                
    #final plotting & saving
    imgname = ' {} Pod Comparsions vs. YPODF4.png'.format(pollutants[n])
    imgpath = os.path.join(path, imgname)
    plt.savefig(imgpath)
    plt.show()