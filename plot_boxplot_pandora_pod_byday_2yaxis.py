# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 12:15:55 2023

Boxplot, but now only keep the dates where both pod & pandora data exist

Split by date on x-axis, colored by Pandora or pod

Different boxplots for each location

These are overlapping boxplots

Split Y-axis

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
        
        # Get the unique dates we have data for
        unique_dates = pandora.index.date
        #also get a column with the unique dates
        pandora['Date'] = pandora.index.strftime('%Y-%m-%d')
       
        #create an array with the data type repeating
        type=np.repeat('Pandora (molec/cm2)',len(pandora))
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
            
            #make sure the index is a datetime
            pod['Date'] = pd.to_datetime(pod.index)
            #also get a column with the unique dates
            pod['Date'] = [t.strftime('%Y-%m-%d') for t in pod['Date']]
           
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
                #data = data.append(pod)
                
            #if the data was pod limited, save it all and note the dates
            else:
                data = data.append(pod)
                #date_range = pd.date_range(start=pod.index.min(), end=pod.index.max(), freq='D',normalize=True)
                mask = (pandora.index > min(pod.index)) & (pandora.index <= max(pod.index))
                #also note the pandora data matching this run
                pandora = pandora.loc[mask]
                #pandora = pandora.loc[date_range, ['{}'.format(pollutants[n])]]
                #and save it
                #data = data.append(pandora)
         
        # create figure and axes objects
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()
        sns.set_style("whitegrid")
        
        #get data from masks to separate pod and pandora data
        
        # create the first boxplot on the left y-axis - Pod
        sns.boxplot(x='Date', y="{}".format(pollutants[n]), data=pod, ax=ax1,
                                   boxprops=dict(facecolor='orange', color='orange'),
                                   whiskerprops=dict(color='orange'),
                                   medianprops=dict(color='gray'),
                                   capprops=dict(color='orange'),
                                   flierprops=dict(markerfacecolor='orange',markeredgecolor='none')
                                   )

        # create the second boxplot on the right y-axis - Pandora
        sns.boxplot(x='Date', y="{}".format(pollutants[n]), data=pandora, ax=ax2,
                                   boxprops=dict(facecolor='lightblue', color='lightblue'),
                                   whiskerprops=dict(color='lightblue'),
                                   medianprops=dict(color='gray'),
                                   capprops=dict(color='lightblue'),
                                   flierprops=dict(markerfacecolor='lightblue',markeredgecolor='none')
                                   )

        # set y-axis labels
        if pollutants[n] == 'O3':
            #ppm for O3
            ax1.set_ylabel('INSTEP {} (ppm)'.format(pollutants[n]),color='r')
        else:
            #ppb for NO2
            ax1.set_ylabel('INSTEP {} (ppb)'.format(pollutants[n]),color='r')
        ax2.set_ylabel('Pandora {} (molec/cm2)'.format(pollutants[n]),color='b')
        #add string + variable for plot title
        titl = '{} {}'.format(locations[i],pollutants[n])
        plt.title(titl)
        
        # rotate x-axis ticks for the first axis
        for tick in ax1.get_xticklabels():
            tick.set_rotation(45)

        # rotate x-axis ticks for the second axis
        for tick in ax2.get_xticklabels():
            tick.set_rotation(45)
        #plt.xticks(rotation = 45)
   
        #final plotting & saving
        imgname = '{}_{}_boxplot_bydate_2yaxis.png'.format(locations[i],pollutants[n])
        imgpath = os.path.join(path, imgname)
        plt.savefig(imgpath)
        plt.show()