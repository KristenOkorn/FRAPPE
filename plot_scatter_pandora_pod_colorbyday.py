# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 12:43:07 2023

Scatterplot of INSTEP vs Pandora data by day - not all merged together

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
    #also set a color for each location
    colors = ['b','g','r']
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
        
        #reformat y to get on the same scale as pod data
        if n == 0:
            #e-20 for ozone
            pandora.iloc[:,0] = pandora.iloc[:,0] * 1e-20
            #add string + variable for x axis
            x = 'Pandora e-20 (molec/cm2)'
        else:
            #e-22 for NO2
            pandora.iloc[:,0] = pandora.iloc[:,0] * 1e-15
            #add string + variable for x axis
            x = 'Pandora e-15 (molec/cm2)' 
            
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
            #rename the column
            pod.columns.values[0] = 'pod'
            
            # Convert the index to a DatetimeIndex and set the nanosecond values to zero
            pod.index = pd.to_datetime(pod.index,errors='coerce')
            
            #get the correct units for each pollutant
            if n == 0:
                #ppm for ozone
                #add string + variable for y axis
                y = 'INSTEP (ppm)'
            else:
                #ppb for NO2
                #add string + variable for y axis
                y = 'INSTEP (ppb)' 
            
            #if the data was pandora limited, pull & save date range we need
            if locations[i] == 'Platteville':
                mask = (pod.index > min(pandora.index)) & (pod.index <= max(pandora.index))
                #also note the pandora data matching this run
                pod = pod.loc[mask]
                #and save it
                data = data.append(pod)
                
        #Merge the data based on datetime index
        merge=pd.merge(pandora,pod,left_index=True,right_index=True)
        
        #Creating axes instance
        plt.rcParams["figure.figsize"] = [6, 5]
        plt.rcParams["figure.autolayout"] = True
        sns.set_style("whitegrid")
    
        # Get the unique dates we have data for
        unique_dates = merge.index.date
       
        # Convert the dates to strings
        merge['date_str'] = merge.index.strftime('%Y-%m-%d')

        #scatter the data
        #plt.scatter(merge['pandora'], merge['pod'],c=colors[i],alpha=0.5)
        
        # Create a scatterplot with separate trendlines for each day
        scatterplot = sns.lmplot(data=merge, x='pandora', y='pod', hue='date_str', palette='rainbow')

        # Don't report negative data
        scatterplot.ax.set_ylim(0, None)
        
        #add string + variable for plot title
        titl = '{} {}'.format(locations[i],pollutants[n])
        plt.title(titl)
        
        #add x & y axis labels
        plt.xlabel(x)
        plt.ylabel(y)  
   
        #final plotting & saving
        imgname = '{}_{}_scatterplot_colorbydate.png'.format(locations[i],pollutants[n])
        imgpath = os.path.join(path, imgname)
        plt.savefig(imgpath)
        plt.show()