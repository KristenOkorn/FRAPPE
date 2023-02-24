# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 15:37:13 2023

@author: okorn
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.collections import PolyCollection
import numpy as np
import os
import pandas as pd
import geopandas as gpd

#create a directory path for us to pull from / save to
path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\P3B CAMS\\'

#load in the 3D CAMS data
filename = "P3_CAMS_location.csv"
# read in the first worksheet from the workbook myexcel.xlsx
filepath = os.path.join(path, filename)
cams = pd.read_csv(filepath,index_col=0)

# Load the shapefile using geopandas
shapefile = gpd.read_file('ne_50m_admin_0_countries.shp')

# Separate multi-part geometries into individual parts
shapefile['geometry'] = shapefile['geometry'].explode()

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the latitude, longitude, and altitude data as a scatter plot
ax.scatter(cams['Latitude'], cams['Longitude'], cams['Altitude'], c=cams['HCHO'], cmap='coolwarm')

# Set the x, y, and z limits of the plot
ax.set_xlim(min(cams['Longitude']), max(cams['Longitude']))
ax.set_ylim(min(cams['Latitude']), max(cams['Latitude']))
ax.set_zlim(0, max(cams['Altitude']))

# Create a globe background
ax.w_xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
ax.w_yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
ax.w_zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
ax.grid(False)
ax.set_facecolor('black')
ax.view_init(elev=30, azim=-60)

globe = ccrs.Globe(semimajor_axis=6370997, semiminor_axis=6370997,
                    ellipse=None)

ocean = cfeature.OCEAN.with_scale('50m')
land = cfeature.LAND.with_scale('50m')
coastline = cfeature.COASTLINE.with_scale('50m')
borders = cfeature.BORDERS.with_scale('50m')

for geom, color in zip([ocean, land, coastline, borders],
                      [cfeature.COLORS['water'], cfeature.COLORS['land'], 'gray', 'gray']):
    polygons = list(geom.geometries())
    collection = PolyCollection(polygons, facecolor=color, edgecolor='none',
                                zorder=0, transform=ccrs.PlateCarree())
    collection.set_array(np.zeros(len(polygons)))
    ax.add_collection3d(collection, zs=np.zeros(len(polygons)), zdir='z')

# Create a PolyCollection for the shapefile
polygons = []
for i, row in shapefile.iterrows():
    if row.geometry.geom_type == 'Polygon':
        polygons.append(row.geometry)
    else:
        polygons.extend(row.geometry)
collection = PolyCollection(polygons, facecolor='none', edgecolor='white',
                            linewidth=0.1, alpha=0.5,
                            transform=ccrs.PlateCarree())
ax.add_collection3d(collection, zs=np.zeros(len(polygons)), zdir='z')

# Show the plot
plt.show()