# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:47:24 2023

Boxplot, but now only keep the dates where both pod & pandora data exist

@author: okorn
"""

#Import helpful toolboxes etc
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import seaborn as sns

#create a directory path for us to pull from / save to
path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\Pandora\\'

#pollutant loop first

#set up pollutant structures to loop through
pollutants = ['O3','NO2']

#loop through for each pollutant
for n in range(len(pollutants)):
    
    #initialize a dataframe to add the concentrations of each to
    data = pd.DataFrame()

    #set up location structures to loop through
    locations = ['BAO','NREL','Platteville']
    #loop through for each location
    for i in range(len(locations)):
        
        #load in the pandora data
        filename = "Pandora_{}_{}.csv".format(locations[i],pollutants[n])
        # read in the first worksheet from the workbook myexcel.xlsx
        filepath = os.path.join(path, filename)
        pandora = pd.read_csv(filepath,index_col=0)
        pandora.index.names = ['datetime']
        # Convert the index to a DatetimeIndex and set the nanosecond values to zero
        pandora.index = pd.to_datetime(pandora.index.values.astype('datetime64[s]'),format="%Y-%m-%d %H:%M:%S",errors='coerce')
        
        #create an array with the location repeating
        place=np.repeat(locations[i], len(pandora))
        #add the array to the individual dataframe
        pandora['Location'] = place.tolist()
       
        #reformat y to get on the same scale as pod data
        if n == 0:
            #e-20 for ozone
            pandora.iloc[:,0] = pandora.iloc[:,0] * 1e-20
            #create an array with the data type repeating
            type=np.repeat('Pandora e-20 (molec)/cm2)',len(pandora))
        else:
            #e-22 for NO2
            pandora.iloc[:,0] = pandora.iloc[:,0] * 1e-15
            #create an array with the data type repeating
            type=np.repeat('Pandora e-15 (molec/cm2)',len(pandora))
       
        #add the array to the individual dataframe
        pandora['type'] = type.tolist()    
        
        #if the data is pandora-limited, save our pandora data now
        if locations[i] == 'Platteville':
            data = data.append(pandora)
            
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
            pod = pd.read_csv(filepath,index_col=0)  
            # remove negatives
            pod = pod[pod.iloc[:, 0] >= 0]
        
            #create an array with the location repeating
            place=np.repeat(locations[i], len(pod))
            #add the array to the individual dataframe
            pod['Location'] = place.tolist()
            
            # Convert the index to a DatetimeIndex and set the nanosecond values to zero
            pod.index = pd.to_datetime(pod.index,format="%m/%d/%Y %H:%M",errors='coerce')
            
            #get the correct units for each pollutant
            if n == 0:
                #ppm for ozone
                #create an array with the data type repeating
                type=np.repeat('INSTEP (ppm)',len(pod))
                #add the array to the individual dataframe
                pod['type'] = type.tolist()
            else:
                #ppb for NO2
                #create an array with the data type repeating
                type=np.repeat('INSTEP (ppb)',len(pod))
                #add the array to the individual dataframe
                pod['type'] = type.tolist()
            
            #if the data was pandora limited, pull & save date range we need
            if locations[i] == 'Platteville':
                mask = (pod.index > min(pandora.index)) & (pod.index <= max(pandora.index))
                #also note the pandora data matching this run
                pod = pod.loc[mask]
                #and save it
                data = data.append(pod)
                
            #if the data was pod limited, save it all and note the dates
            else:
                data = data.append(pod)
                #date_range = pd.date_range(start=pod.index.min(), end=pod.index.max(), freq='D',normalize=True)
                mask = (pandora.index > min(pod.index)) & (pandora.index <= max(pod.index))
                #also note the pandora data matching this run
                pandora = pandora.loc[mask]
                #pandora = pandora.loc[date_range, ['{}'.format(pollutants[n])]]
                #and save it
                data = data.append(pandora)
                
    #Creating axes instance
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    sns.set_style("whitegrid")
    #create a custom palette to color our boxes
    ax = sns.boxplot(x="Location", y="{}".format(pollutants[n]), data=data,hue='type')
    #plt.ylim(0, 2)

    #add string + variable for y axis, plus limits
    y = '{}'.format(pollutants[n])
    plt.ylabel(y)
    
    #add string + variable for plot title
    titl = '{} {}'.format(locations[i],pollutants[n])
    plt.title(titl)
   
    #final plotting & saving
    imgname = '{}_boxplot_talign.png'.format(pollutants[n])
    imgpath = os.path.join(path, imgname)
    plt.savefig(imgpath)
    plt.show()