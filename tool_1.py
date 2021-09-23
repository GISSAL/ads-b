# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_1.pyt
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  ArcGIS script tool code that reads raw ADS-B data from the logger, creates "flights", and calculates new variables
    Status:  Development
    Date created: 9/16/2021
    Date last modified: 9/17/2021
    Python Version: 3.7
"""


# Import libraries
import arcpy
import pandas as pd
import numpy as np

# Local variable(s)
park_name = arcpy.GetParameterAsText(0)         
input_file = arcpy.GetParameterAsText(1)        
input_file_date = arcpy.GetParameterAsText(2)
output_workspace = arcpy.GetParameterAsText(3)
dur_threshold = arcpy.GetParameterAsText(4)

# Custom Function 1 - Vectorized Haversine function to calculate great circle distance between successive locations
# Slightly modified version of https://towardsdatascience.com/heres-how-to-calculate-distance-between-2-geolocations-in-python-93ecab5bbba4
def haversine_distance(lat1, lon1, lat2, lon2):
   r = 6371000  #meters
   phi1 = np.radians(lat1)
   phi2 = np.radians(lat2)
   delta_phi = np.radians(lat2 - lat1)
   delta_lambda = np.radians(lon2 - lon1)
   a = np.sin(delta_phi / 2)**2 + np.cos(phi1) * np.cos(phi2) *   np.sin(delta_lambda / 2)**2
   res = r * (2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))
   return np.round(res, 2)

# Custom Function 2 - Heading function to calculate the bearing between two successive locations
# Slightly modified version of https://stackoverflow.com/questions/54873868/python-calculate-bearing-between-two-lat-long
def get_bearing(lat1, long1, lat2, long2):
    dLon = (long2 - long1)
    x = np.cos(np.radians(lat2)) * np.sin(np.radians(dLon))
    y = np.cos(np.radians(lat1)) * np.sin(np.radians(lat2)) - np.sin(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.cos(np.radians(dLon))
    brng = np.arctan2(x,y)
    brng = np.degrees(brng)
    compass_brng = (brng + 360) % 360
    return compass_brng

# Read in ADS-B text file
data = pd.read_csv(input_file, sep="\t")

# Transform DateTime field from character to datetime objects in UTC
data["DateTime"] = pd.to_datetime(data["DateTime"])

# Sort records by HexID and DateTime
data.sort_values(["HexID", "DateTime"], inplace=True)

# Reset dataframe index after sorting
data = data.reset_index(drop=True)

# Calculate intitial time difference between sequential waypoints for each aircraft
data["Dur_Secs"] = data.groupby("HexID")["DateTime"].diff().dt.total_seconds()
data["Dur_Secs"] = data["Dur_Secs"].fillna(-99)

# Create new series to store FlightID data
data["FlightID"] = ""

# Assign FlightID based on waypoint duration threshold
count = 1
for index in data.index:
    if data.loc[index, "Dur_Secs"] < float(dur_threshold):
        data.loc[index, "FlightID"] = data.loc[index, "HexID"] + "_" + str(count)
    else:
        count += 1
        data.loc[index, "FlightID"] = data.loc[index, "HexID"] + "_" + str(count)

# Recalculate time difference between sequential waypoints for each flight
data["Dur_Secs"] = data.groupby("FlightID")["DateTime"].diff().dt.total_seconds()
data["Dur_Secs"] = data["Dur_Secs"].fillna(-99)

# Apply haversine_distance function to calculate distance between successive waypoints in meters
data["Dist_Meters"] = haversine_distance(data.Latitude.shift(), data.Longitude.shift(), data.loc[1:, 'Latitude'], data.loc[1:, 'Longitude'])

# Calculate and add field for aircraft speed in meters/second
data["Speed"] = data["Dist_Meters"] / data["Dur_Secs"]

# Apply get_bearing function to calculate distance between successive waypoints in meters
data["Bearing_Degs"] = get_bearing(data.Latitude.shift(), data.Longitude.shift(), data.loc[1:, 'Latitude'], data.loc[1:, 'Longitude'])

# Apply null value to distance, speed, and bearing fields if duration is null
for index in data.index:
    if data.loc[index, "Dur_Secs"] == -99:
        data.loc[index, "Dist_Meters"] = -99
        data.loc[index, "Bearing_Degs"] = -99
        data.loc[index, "Speed"] = -99

# Write output file
data.to_csv(output_workspace + "\ADSB_" + park_name + "_" + input_file_date + ".csv")
