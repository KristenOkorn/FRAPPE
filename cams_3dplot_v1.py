# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 15:37:13 2023

@author: okorn
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Polygon
from matplotlib.collections import PolyCollection
import numpy as np
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPolygon

#create a directory path for us to pull from / save to
path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\P3B CAMS\\'

#load in the 3D CAMS data
filename = "P3_CAMS_location.csv"
# read in the first worksheet from the workbook myexcel.xlsx
filepath = os.path.join(path, filename)
cams = pd.read_csv(filepath,index_col=0)

# Define the proj4 string for EPSG:4326
proj_str = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

# Create a Point object from the latitude and longitude data
cams['geometry'] = [Point(xy) for xy in zip(cams.Longitude, cams.Latitude)]
# Create a GeoDataFrame from the dataframe
gdf = gpd.GeoDataFrame(cams, geometry='geometry', crs='EPSG:4326')

# Load the shapefile using geopandas
shapefile_path = r'C:\Users\okorn\Documents\GIS\ne_50m_admin_0_countries.shp'
shapefile = gpd.read_file(shapefile_path)

# Separate multi-part geometries into individual parts
exploded_shapes = shapefile.explode()

# Drop any rows with null values
exploded_shapes = exploded_shapes.dropna(subset=['geometry'])

# Reset the index to avoid duplicate label error
exploded_shapes = exploded_shapes.reset_index(drop=True)

# Re-assign the exploded shapes to the original shapefile
shapefile = shapefile.reindex(exploded_shapes.index)
shapefile['geometry'] = exploded_shapes['geometry']

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

# Set the x & y limits of the plot
ax.set_xlim(min(cams['Longitude']), max(cams['Longitude']))
ax.set_ylim(min(cams['Latitude']), max(cams['Latitude']))

# Plot the latitude, longitude, and altitude data as a scatter plot
ax_3d = fig.add_subplot(111, projection='3d')
ax_3d.scatter(cams['Longitude'], cams['Latitude'], cams['Altitude'], c=cams['HCHO'], cmap='coolwarm')

#add a z label
ax_3d.set_zlabel('Altitude (ft)')
# Set the projection extent
ax.set_global()

# Create a globe background
ax.background_patch.set_visible(False)
ax.outline_patch.set_visible(False)
ax.set_facecolor('black')
ax.set_global()

globe = ccrs.Globe(semimajor_axis=6370997, semiminor_axis=6370997, ellipse=None)

ocean = cfeature.OCEAN
land = cfeature.LAND
coastline = cfeature.COASTLINE
borders = cfeature.BORDERS

for geom, color in zip([ocean, land, coastline, borders], 
                       [cfeature.COLORS['water'], cfeature.COLORS['land'], 'gray', 'gray']):
    polygons = []
    for p in geom.geometries():
        if isinstance(p, Polygon):
            polygons.append(p)
        elif isinstance(p, MultiPolygon):
            for q in p:
                polygons.append(q)

    collection = PolyCollection(polygons, facecolor=color, edgecolor='none',
                                zorder=0, transform=ccrs.PlateCarree())
    collection.set_array(np.zeros(len(polygons)))
    if isinstance(ax, Axes3D):
        ax.add_collection3d(collection, zs=np.zeros(len(polygons)), zdir='z')
    else:
        ax.add_collection(collection)
        
# Create a colorbar
sm = plt.cm.ScalarMappable(cmap='coolwarm')
sm.set_array(cams['HCHO'])

# Create a separate axes object for the colorbar
cax = fig.add_axes([1.1, 0.2, 0.02, 0.6])

# Add the colorbar to the separate axes object
cbar = plt.colorbar(sm, cax=cax)

# Add label to colorbar
cbar.set_label('HCHO (pptv)')

# Adjust the position of the colorbar labels
cax.yaxis.set_ticks_position('left')
cax.yaxis.set_label_position('left')

#final plotting & saving
imgname = 'HCHO_3d_flightpath.png'
imgpath = os.path.join(path, imgname)
plt.savefig(imgpath, bbox_inches='tight', pad_inches=0.1)
plt.show()
