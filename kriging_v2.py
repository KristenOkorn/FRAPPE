# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 10:23:34 2023

@author: okorn
"""

#Import necessary toolboxes
import os
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from scipy.linalg import solve
from sklearn.metrics.pairwise import pairwise_kernels
import matplotlib.pyplot as plt
import imageio
from matplotlib.colors import Normalize

#pollutant loop first

#set up pollutant structures to loop through
pollutants = ['O3','NO2','HCHO']

#loop through for each pollutant
for n in range(len(pollutants)):
    
    #create a directory path for us to pull from / save to
    path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\Kriging\\{}'.format(pollutants[n])

    #Get the list of files from this directory
    from os import listdir
    from os.path import isfile, join
    fileList = [f for f in listdir(path) if isfile(join(path, f))]
    
    #iterate over each file in the main folder
    for i in range(len(fileList)-1):
        
        #Create full file path for reading file
        filePath = os.path.join(path, fileList[i])
        
        #load in the file
        pod = pd.read_csv(filePath)
        
        #get the pod name by itself
        podName = fileList[i][:6]
        
        #------Get concentration data------
        #if ozone, convert to ppb for pods
        #regulatory already in ppb
        if pollutants[n] == 'O3' and 'YPOD' in fileList[i]:
            pod['O3'] = pod['O3'] * 1000
        
        #rename the observed values
        pod = pod.rename(columns= {'{}'.format(pollutants[n]) : '{}_{}'.format(podName,pollutants[n])})
        
        # Convert the index to a DatetimeIndex and set the nanosecond values to zero
        pod.index = pd.to_datetime(pod['datetime'],errors='coerce')
    
        #drop the original datetime column
        pod = pod.drop(columns=['datetime'])
    
        #resample to hourly for kriging
        pod = pod.resample('H').mean()
        
        # remove negatives
        pod = pod[pod.iloc[:, 0] >= 0]
        
        #if this is the first iteration, make our dataframe the first
        if i == 0:
            data = pod
        #otherwise merge it with the existing ones
        else:
            data = data.merge(pod, on='datetime', how='outer')
        
        #------Get matching location data------
        #get the kriging location log from the main directory
        kriging_path = 'C:\\Users\\okorn\\Documents\\FRAPPE\\Kriging\\'
        location_filename = 'Kriging_locations.csv'
        
        #Create full file path for reading file
        location_filePath = os.path.join(kriging_path, location_filename)
        
        #load in the file
        location_data = pd.read_csv(location_filePath)
        
        #if this is the first pod, make our 'locations' array
        if i == 0:
            locations = np.zeros((len(location_data),2))
        
        #Create a filtered dataframe to make sure we have location data
        filtered_df = location_data[location_data["PodName"] == podName]
        
        #Make sure this data is available in our dataframe
        if not filtered_df.empty:
            #get the index of our current pod name
            pod_index = location_data[location_data["PodName"] == podName].index.item()
            locations[i] = [location_data['Latitude'][pod_index], location_data['Longitude'][pod_index]]
        #If we don't have location info for this pod, delete it from the main dataframe
        else:
            data = data.drop(columns=['{}_{}'.format(podName,pollutants[n])])
    
    #Remove any rows still containing 0 in the 'location' array
    locations = locations[~np.any(locations == 0, axis=1)]
    
    #Remove any lat/long values that sneak in here
    if 'Latitude' in data.columns:
        data = data.drop(columns=['Latitude_x','Longitude_x','Latitude_y','Longitude_y','Latitude','Longitude'])
     
    #Remove rows where all values are NaN
    data = data[~np.all(np.isnan(data), axis=1)]

    #reformat our data into "observed values"
    observed_values=data.values
    
    #get the indicdes of any regulatory observations in our dataframe
    high_weight_indices = [idx for idx, col in enumerate(data.columns) if 'YPOD' not in col]
                            
    #------Convert lat/long to distance------
    #Haversine formula for calculating distance between two points on a sphere
    def haversine_distance(coords1, coords2):
        lat1, lon1 = coords1
        lat2, lon2 = coords2
        R = 6371.0  # Earth radius in kilometers
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c
        return distance

    #------Simple Kriging------
    def simple_kriging(target_location, locations, observed_values, cov_model='squared_exponential', range_val=1.0, nugget=0.1):
        #Handle NaNs in observed values
        valid_indices = np.where(~np.isnan(observed_values))[0]
        locations = locations[valid_indices]
        observed_values = observed_values[valid_indices]

        if cov_model == 'squared_exponential':
            cov_matrix = pairwise_kernels(locations, locations, metric='rbf', gamma=1.0 / (2 * range_val**2))
        else:
            raise ValueError("Unsupported covariance model")

        weights = solve(cov_matrix + nugget * np.eye(len(locations)), np.ones(len(locations)))
        weights /= np.sum(weights)

        estimated_value = np.dot(weights, observed_values)
        return estimated_value
    
        if high_weight_indices is not None:
            #Apply higher weights to regulatory measurements
            estimated_value[high_weight_indices] *= 2.0  # You can adjust the weight factor as needed
    
    #------Gridding------
    min_lat = min(locations[:, 0])
    max_lat = max(locations[:, 0])
    min_lon = min(locations[:, 1])
    max_lon = max(locations[:, 1])

    #Assuming 1 km is approximately 0.009 degrees for both latitude and longitude
    #So 5 km = 0.045
    lat_vals = np.arange(min_lat, max_lat + 0.045, 0.045)
    lon_vals = np.arange(min_lon, max_lon + 0.045, 0.045)

    grid_locations = np.array(np.meshgrid(lat_vals, lon_vals)).T.reshape(-1, 2)

    #------Estimate at each location------
    # Loop through time instances and create a GIF
    gif_images = []

    for time_instance in range(observed_values.shape[0]):
        
        #-----Ignore NaNs in the current row-----
        #Get the indices of NaN values in the specified row
        nan_indices = np.where(np.isnan(observed_values[time_instance]))[0]
        
        #Estimate values for each target location
        estimated_values = []
        for loc in grid_locations:
            estimated_value = simple_kriging(loc, locations, observed_values[time_instance])
            estimated_values.append(estimated_value)

        #Convert the list to a NumPy array
        estimated_values = np.array(estimated_values).reshape(len(lat_vals), len(lon_vals))  # Reshape for pcolormesh
        
        #Create meshgrid arrays for X and Y coordinates
        lon_mesh, lat_mesh = np.meshgrid(lon_vals, lat_vals)

        #------Visualization------
        #only want to visualize if estimated_value exists
        if estimated_value is not None:
        
            #Initialize plotting
            fig, ax = plt.subplots() 
            
            #Use pcolormesh to create colored squares
            pcm = ax.pcolormesh(lon_mesh, lat_mesh, estimated_values, cmap='viridis', edgecolors='k')
            
            #layer the observed values on top
            #scatter = plt.scatter(locations[:, 1], locations[:, 0], c=observed_values[time_instance], cmap='viridis', marker='o', label='Sensor', edgecolors='k')
            
            #layer the pod data on top
            #Create a boolean mask to exclude columns at high_weight_indices
            mask = np.ones(observed_values.shape[1], dtype=bool)
            mask[high_weight_indices] = False

            #Apply the boolean mask and select the specified column
            pod_obs = observed_values[:,mask]
            
            #Create a boolean mask to exclude rows at high_weight_indices for lat/lon
            mask = np.ones(locations.shape[0], dtype=bool)
            mask[high_weight_indices] = False
            
            #Apply the mask to the lat/lon values
            pod_lat = locations[mask,0] #y
            pod_lon = locations[mask,1] #x
            
            #now scatter the pod data
            scatter = plt.scatter(pod_lon, pod_lat, c=pod_obs[time_instance], cmap='viridis', marker='o', label='Sensor', edgecolors='k')
            
            #----Mask & plot regulatory data----
            #same deal for the regulatory data
            #Create a boolean mask to exclude columns at high_weight_indices
            mask = np.zeros(observed_values.shape[1], dtype=bool)
            mask[high_weight_indices] = True
            
            #Apply the boolean mask and select the specified column
            reg_obs = observed_values[:,mask]
            
            #Create a boolean mask to exclude rows at high_weight_indices for lat/lon
            mask = np.zeros(locations.shape[0], dtype=bool)
            mask[high_weight_indices] = True
            
            #Apply the mask to the lat/lon values
            reg_lat = locations[mask,0] #y
            reg_lon = locations[mask,1] #x
            
            #Get the range of values for color limits
            observed_min, observed_max = np.nanmin(observed_values), np.nanmax(observed_values)
            estimated_min, estimated_max = np.nanmin(estimated_values), np.nanmax(estimated_values)
            
            #now scatter the regulatory data
            scatter = plt.scatter(reg_lon, reg_lat, c=reg_obs[time_instance], cmap='viridis', marker='o', label='Regulatory', edgecolors='w')
            
            #Set color limits for both scatter plot and pcolormesh plot
            scatter.set_clim(vmin=min(observed_min, estimated_min), vmax=max(observed_max, estimated_max))
            pcm.set_clim(vmin=min(observed_min, estimated_min), vmax=max(observed_max, estimated_max))
        
            #Labels & axes
            plt.colorbar(scatter, label='{} (ppm)'.format(pollutants[n]))
            legend = plt.legend()
            legend.get_frame().set_facecolor('gray')
            ax.set_xticklabels(locations[:, 1],rotation=45)
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.title('Kriging Interpolation - {} - {}'.format(pollutants[n],data.index[time_instance]))
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
            
            #Save the current plot as an image
            image_filename = os.path.join(path, 'frame_{}_{}.png'.format(pollutants[n], time_instance))
            plt.savefig(image_filename,dpi=300)
            
            #show should come after saving
            plt.show()
            plt.close()  # Close the current plot to avoid memory leaks

            #Append the filename to the list of images
            gif_images.append(image_filename)

    #Save the GIF file using imageio
    gif_filename = os.path.join(path, 'kriging_estimates_{}.gif'.format(pollutants[n]))
    imageio.mimsave(gif_filename, [imageio.imread(image) for image in gif_images], duration=0.2)

    #Clean up: Remove the individual image files
    for image in gif_images:
        os.remove(image)