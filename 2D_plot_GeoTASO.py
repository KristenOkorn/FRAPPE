# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 16:49:30 2023

@author: okorn
"""

# %% load libraries and files
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import cartopy.crs as ccrs
import cartopy.feature as cf
import cartopy.io.shapereader as shpreader
import os

#create a directory path for us to pull from / save to
path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\GeoTASO\\'
csvpath = 'C:\\Users\\okorn\\Documents\\FRAPPE\\GeoTASO\\NO2 Data csv'

#loop through each file
#Get the list of files from this directory
from os import listdir
from os.path import isfile, join
fileList = [f for f in listdir(csvpath) if isfile(join(csvpath, f))]

#iterate over each file in the main folder
for i in range(len(fileList)):
    
    #Create full file path for reading file
    filePath = os.path.join(csvpath, fileList[i])
    
    #Get just the date for this file
    date = fileList[i][40:50]
    
    #set up pollutant structures to loop through
    pollutants = ['NO2_slant','NO2_below']
    #get the units matching this measurement
    units = ['molec/cm2','molec/cm2']

    #loop through for each pollutant
    for n in range(len(pollutants)):

        #load in the geotaso data
        gtas = pd.read_csv(filePath,index_col=0)  
        

        # ------------------ 2D Flight Map ------------------
        #initialize figure and projection
        fig4 = plt.figure(4)
        projection = ccrs.Mercator()

        #add in standard geographies
        ax4 = plt.axes(projection=projection)
        ax4.add_feature(cf.COASTLINE)
        ax4.add_feature(cf.BORDERS)
        ax4.add_feature(cf.OCEAN)
        ax4.add_feature(cf.LAND)
        ax4.add_feature(cf.LAKES)
        ax4.add_feature(cf.RIVERS)

        #add in a geography we're creating - county lines
        shp_path = os.path.join(path, 'countyl010g.shp')
        reader = shpreader.Reader(shp_path)
        counties = list(reader.geometries())
        COUNTIES = cf.ShapelyFeature(counties, ccrs.PlateCarree())
        ax4.add_feature(COUNTIES, facecolor='none', edgecolor='gray')

        #add these geographies and our scatter to the plot
        plate = ccrs.PlateCarree()
        sc1 = ax4.scatter(gtas['longitude'].values, gtas['latitude'].values,
                  c=gtas['{}'.format(pollutants[n])], s=15, transform=plate)

        #formatting
        cb1 = plt.colorbar(sc1)
        cb1.set_label('{} ({})'.format(pollutants[n],units[n]), fontsize=10)
        cb1.ax.tick_params(labelsize=10)
        fig4.tight_layout()

        #set title
        ax4.set_title('{} {} ({})'.format(date,pollutants[n],units[n]))

        #final plotting & saving
        imgname = '{}_{}_flight_tracks.png'.format(date,pollutants[n])
        imgpath = os.path.join(path, imgname)
        plt.savefig(imgpath)
        plt.show()

        # ------------------ Vertical Profile ------------------
        #initialize axes/plot
        fig5, ax5 = plt.subplots(1, figsize=(5, 4), dpi=200)

        # Convert the index to a DatetimeIndex and set the nanosecond values to zero
        gtas.index = pd.to_datetime(gtas.index.values.astype('datetime64[s]'),format="%Y-%m-%d %H:%M:%S",errors='coerce')
        # Convert the dates to strings
        gtas['date_str'] = pd.to_numeric(gtas.index.strftime("%Y%m%d%H%M%S"))

        #create the plot
        sc2 = plt.scatter(gtas['{}'.format(pollutants[n])], gtas['altitude'], c=gtas.index)

        #formatting
        plt.xlabel('{} ({})'.format(pollutants[n],units[n]))
        ax5.grid()
        cb2 = plt.colorbar(sc2)
        cb2.ax.set_yticklabels(pd.to_datetime(cb2.get_ticks()).strftime(date_format='%H:%M'))
        cb2.set_label('Time (UTC)')
        plt.ylabel('Altitude (m)')
    
        #set title
        ax5.set_title('{} {} ({})'.format(date,pollutants[n],units[n]))

        #final plotting & saving
        imgname = '{}_{}_vertical_profile.png'.format(date,pollutants[n])
        imgpath = os.path.join(path, imgname)
        plt.savefig(imgpath)
        plt.show()
