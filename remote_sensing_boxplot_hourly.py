# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 18:10:20 2022

@author: okorn
"""

#Import helpful toolboxes etc
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import numpy as np

#set up pollutant structures to loop through
pollutants = ['O3','NO2']

#loop through for each pollutant
for n in range(len(pollutants)):

    #create a directory path for us to pull from / save to
    path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\Pandora\\'

    locations = ['BAO','NREL','Platteville']
    #loop through for each location
    for i in range(len(locations)):
    
        #load in the remote sensing data

        #get the filename to be loaded
        filename = "Pandora_{}_{}.csv".format(locations[i],pollutants[n])
        #filename = "{}_partialcolumn_{}.xlsx".format(locations[i],pollutants[n])
        #read in the first worksheet from the workbook myexcel.xlsx
        filepath = os.path.join(path, filename)
        rs = pd.read_csv(filepath, index_col=0)  

        #make sure the index is a datetime
        rs.index = pd.to_datetime(rs.index)
        
        #create a new column to add our hour of day to
        rs["hours"] = pd.NaT
        #get the hours alone
        hours = rs.index.hour
        #convert to pacific daylight time
        hours = hours -7
        #now correct the negatives
        hours = np.where(hours < 0, hours + 24 , hours)
        
        #add in dummy hour data so it doesn't skip the non-daylight hours
        dummy = [0,1,2,3,4,5,20,21,22,23]
        hours = np.append(hours,dummy)
        for j in range(len(dummy)):
            rs.loc[len(rs)] = -100

        #Creating axes & histogram
        plt.rcParams["figure.figsize"] = [7.50, 3.50]
        plt.rcParams["figure.autolayout"] = True
        sns.set_style("whitegrid")
        sns.set_color_codes(palette='pastel')
        ax = sns.boxplot(y=rs["{}".format(pollutants[n])], x=hours, color = 'b')

        #add string + variable for y axis & plot title
        if pollutants[n] == 'O3':
            y = '$O_3$ (ppb)'
            titl = "Pandora $O_3$ - {}".format(locations[i])
        else:
            y = '$NO_2$ (ppm)'
            titl = "Pandora $NO_2$ - {}".format(locations[i])
        plt.ylabel(y)
        plt.title(titl)
    
        #add string + variable for x axis, plus limits
        x = 'Hour of Day (PDT)'
        plt.xlabel(x)
   
        #final plotting & saving
        imgname = 'Pandora_{}_{}_boxplot_hourly.png'.format(locations[i],pollutants[n])
        imgpath = os.path.join(path, imgname)
        plt.savefig(imgpath)
        plt.show()