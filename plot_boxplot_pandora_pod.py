# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 16:17:15 2023

@author: okorn
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 09:19:38 2022

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
        #add this location to the overall dataframe
        data = data.append(pandora)
        
        #get the pod names matching each location
        if locations[i] == 'BAO':
            pods = ['YPODD4','YPODF3']
        elif locations[i] == 'NREL':
            pods = ['YPODF1']
        else:
            pods = ['YPODF4','YPODF9']
        
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
            
            #get the correct units for each pollutant
            if n == 0:
                #ppm for ozone
                #create an array with the data type repeating
                type=np.repeat('INSTEP (ppm)',len(pod))
            else:
                #ppb for NO2
                #create an array with the data type repeating
                type=np.repeat('INSTEP (ppb)',len(pod))
                
            #create an array with the data type repeating
            type=np.repeat('INSTEP',len(pod))
            #add the array to the individual dataframe
            pod['type'] = type.tolist()
            #add this location to the overall dataframe
            data = data.append(pod)
        
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
    imgname = '{}_boxplot.png'.format(pollutants[n])
    imgpath = os.path.join(path, imgname)
    plt.savefig(imgpath)
    plt.show()