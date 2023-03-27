# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 20:27:18 2023

Scatterplot of Pod vs. Pod - BAO

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
#pods = ['YPODD4','YPODD6','YPODD8','YPODF1','YPODF3','YPODF7','YPODF8','YPODF9','YPODN4','YPODN5','YPODN7','YPODN8']
pods = ['YPODF3','YPODD8','YPODN4','YPODN8']
#colors = ['red', 'green', 'blue', 'orange', 'purple', 'pink', 'brown', 'gray','m','k','aquamarine','mediumseagreen']
colors = ['red', 'green', 'blue', 'orange']

#loop through for each pollutant
for n in range(len(pollutants)):
    
    # create a 2x2 grid of subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 10))
    # flatten the axes array for easy iteration
    axes = axes.flatten()
    #add extra whitespace between subplots
    fig.subplots_adjust(wspace=0.3, hspace=0.5)
    
    #load in the main pod data
    filename = "YPODD4_{}.csv".format(pollutants[n])
    # read in the first worksheet from the workbook myexcel.xlsx
    filepath = os.path.join(path, filename)
    main_pod = pd.read_csv(filepath,index_col=0)
    main_pod.index.names = ['datetime']
    main_pod.columns.values[0] = 'pod_main'
    #get rid of negatives
    main_pod = main_pod.drop(main_pod[main_pod['pod_main'] < 0].index)
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
        #now get the comparative data from the other pandoras
        filename = "{}_{}.csv".format(pods[i],pollutants[n])
        # read in the first worksheet from the workbook myexcel.xlsx
        filepath = os.path.join(path, filename)
        pod = pd.read_csv(filepath,index_col=0)
        pod.index.names = ['datetime']
        pod.columns.values[0] = 'pod'
        #get rid of negatives
        pod = pod.drop(pod[pod['pod'] < 0].index)
        # Convert the index to a DatetimeIndex and set the nanosecond values to zero
        pod.index = pd.to_datetime(pod.index,errors='coerce')
    
        #Merge the data from both pandoras
        merge=pd.merge(main_pod,pod,left_index=True,right_index=True)
                
        axes[i].scatter(merge['pod_main'], merge['pod'],c=colors[i],alpha=0.5)
            
        #add trendline
        if not merge.empty:
            z = np.polyfit(merge['pod_main'], merge['pod'], 1) #calculate equation for trendline
            p = np.poly1d(z) #calculate points
            axes[i].plot(merge['pod_main'], p(merge['pod_main']),c=colors[i]) #add trendline to plot
    
        #add string + variable for plot title
        titl = '{} {}'.format(pods[i],pollutants[n])
        axes[i].set_title(titl)
        fig.suptitle("Platteville INSTEP Comparison", fontsize=16)
        
        #add x & y axis labels
        x = 'YPODF3 {} ({})'.format(pollutants[n],units[n])
        axes[i].set_xlabel(x)
        y = '{} {} ({})'.format(pods[i],pollutants[n],units[n])
        axes[i].set_ylabel(y)  
                
    #final plotting & saving
    imgname = 'BAO Area {} Pod Comparsions.png'.format(pollutants[n])
    imgpath = os.path.join(path, imgname)
    plt.savefig(imgpath)
    plt.show()