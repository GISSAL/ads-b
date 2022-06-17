# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_1.py
    Author: Shawn Hutchinson
    Credits: Damon Joyce, Shawn Hutchinson, Brian Peterson
    Description:  ArcGIS script tool code that reads raw ADS-B data from the logger, creates unique flights, and generates output CSV for later GIS operations
    Status:  Development
    Date created: 10/6/2021
    Date last modified: 6/17/2022
    Python Version: 3.7
"""

# Import libraries
import arcpy, os, pandas as pd, time

## User-specified local variable(s) for ArcGIS script tool
park_name = arcpy.GetParameterAsText(0)
input_file = arcpy.GetParameterAsText(1)
dur_threshold = arcpy.GetParameterAsText(2)
output_workspace = arcpy.GetParameterAsText(3)

# Start timer
start = time.time()

# Read in ADS-B text file
data = pd.read_csv(input_file, sep="\t")

# Keep only records with valid values
data = data.dropna(how = 'all')

# Ensure remaining field values are in numeric format
if data["lat"].dtypes != "int64":
    data["lat"].astype("int")
else:
    pass

if data["lon"].dtypes != "int64":
    data["lon"].astype("int")
else:
    pass

if data["altitude"].dtypes != "int64":
    data["altitude"].astype("int")
else:
    pass

if data["heading"].dtypes != "int64":
    data["heading"].astype("int")
else:
    pass

if data["hor_velocity"].dtypes != "int64":
    data["hor_velocity"].astype("int")
else:
    pass

if data["ver_velocity"].dtypes != "int64":
    data["ver_velocity"].astype("int")
else:
    pass

if data["tslc"].dtypes != "int64":
    data["tslc"].astype("int")
else:
    pass

# Unpack TSLC data
flags_names = ["valid_BARO", "valid_VERTICAL_VELOCITY", "SIMULATED_REPORT", "valid_IDENT", "valid_CALLSIGN", "valid_VELOCITY", "valid_HEADING", "valid_ALTITUDE", "valid_LATLON"]
flags = data["validFlags"].apply(lambda t: list(bin(int(t, 16))[2:].zfill(9)[-9:]))
flags_df = pd.DataFrame(list(flags), columns=flags_names).replace({'0': False, '1': True})
data = pd.concat([data.drop('validFlags', axis=1), flags_df], axis=1)


# Keep only records with TSLC values of 1 or 2
invalidTslc = len(data.query("tslc >= 3 or tslc == 0")) / data.shape[0] * 100
data.drop(data[data["tslc"] >= 3].index, inplace = True)
data.drop(data[data["tslc"] == 0].index, inplace = True)

# Keep only records with valid latlon and alitude
invalidAltitude = round(data["valid_ALTITUDE"].value_counts(normalize=True)[0] * 100, 2)
invalidLatLon = round(data["valid_LATLON"].value_counts(normalize=True)[0] * 100, 2)
data.drop(data[data["valid_LATLON"] == "False"].index, inplace = True)
data.drop(data[data["valid_ALTITUDE"] == "False"].index, inplace = True)
print("Data screened for valid TSLC, Altidude, and Lat/Lon Coordinates...")
arcpy.AddMessage("Data screened for valid TSLC, Altitudes, and Lat/Lon Coordinates...")

# Convert Unix timestamp to datetime objects in UTC and re-scale selected int values 
data["TIME"] = pd.to_datetime(data["TIME"], unit = "s")
data["DATE"] = data["TIME"].dt.strftime("%Y%m%d")
data["lat"] = data["lat"] / 1e7
data["lon"] = data["lon"] / 1e7
data["altitude"] = data["altitude"] / 1e3
data["heading"] = data["heading"] / 1e2
data["hor_velocity"] = data["hor_velocity"] / 1e2
data["ver_velocity"] = data["ver_velocity"] / 1e2
print("ADS-B field data types formatted...")
arcpy.AddMessage("ADS-B field data types formatted...")

# Sort records by ICAO Address and TIME then reset dataframe index
data.sort_values(["ICAO_address", "TIME"], inplace=True)
data = data.reset_index(drop=True)
print("ADS-B records sorted by ICAO Address and Time...")
arcpy.AddMessage("ADS-B records sorted by ICAO Address and Time...")

# Calculate time difference between sequential waypoints for each aircraft
data["dur_secs"] = data.groupby("ICAO_address")["TIME"].diff().dt.total_seconds()
data["dur_secs"] = data["dur_secs"].fillna(0)

# Count then delete identical waypoints based on ICAO_address, time, lat, and lon
duplicateWaypoints = 100 - (len(data.drop_duplicates(subset=['ICAO_address', 'TIME', 'lat', 'lon'])) / len(data) * 100)
data.drop_duplicates(subset=['ICAO_address', 'TIME', 'lat', 'lon'], keep = 'last')
print("Identical waypoints removed...")
arcpy.AddMessage("Identical waypoints removed...")

# Use threshold waypoint duration value to identify separate flights by aircraft, then sum the number of "true" conditions to assign unique ID
data['diff_flight'] = data['dur_secs'] >= 900
data['cumsum'] = data.groupby('ICAO_address')['diff_flight'].cumsum()
data['flight_id'] = data['ICAO_address'] + "_" + data['cumsum'].astype(str) + "_" + data['DATE']       

# Remove records where there is only one recorded waypoint
data = data[data.groupby("flight_id").flight_id.transform(len) > 1]
print("Separate flights by same aircraft identified...")
arcpy.AddMessage("Separate flights by same aircraft identified...")

# Remove fields that are no longer needed
data = data.drop(columns = ['tslc', 'dur_secs', 'diff_flight', 'cumsum', 'valid_BARO', 'valid_VERTICAL_VELOCITY', 'SIMULATED_REPORT', 'valid_IDENT', 'valid_CALLSIGN', 'valid_VELOCITY', 'valid_HEADING', 'valid_ALTITUDE', 'valid_LATLON', 'DATE'])
print("Unused attribute fields removed...")
arcpy.AddMessage("Unneeded attribute fields and flags removed...")

# Write output file in CSV format
base = os.path.basename(input_file)
data.to_csv(output_workspace + "\ADSB_" + park_name + "_" + os.path.splitext(base)[0] + ".csv")
print("Success... ADS-B data cleaned and formatted output file created.")
arcpy.AddMessage("Success... ADS-B data cleaned and formatted output file created!")

# Report QA/QC data, aircraft and flight summaries, and execution time
aircraft = data["ICAO_address"].unique()
flights = data["flight_id"].unique()
end = time.time()
print("Percent of original waypoints eliminated by TSLC: {0}".format(str(round(invalidTslc, 2))))
arcpy.AddMessage("Percent of original waypoints eliminated by TSLC: {0}".format(str(round(invalidTslc,2))))
print("Percent of duplicate waypoints: {0}".format(str(round(duplicateWaypoints,2))))
arcpy.AddMessage("Percent of duplicate waypoints: {0}".format(str(round(duplicateWaypoints,2))))
print("Percent of original waypoints with invalid altitudes: {0}".format(str(invalidAltitude)))
arcpy.AddMessage("Percent of original waypoints with invalid altitudes: {0}".format(str(invalidAltitude)))
print("Percent of waypoints with invalid x,y coordinates: {0}".format(str(invalidLatLon)))
arcpy.AddMessage("Percent of waypoints with invalid x,y coordinates: {0}".format(str(invalidLatLon)))
print("Total Unique Aircraft in Input File: {0}".format(len(aircraft)))
arcpy.AddMessage("Total Unique Aircraft in Input File: {0}".format(len(aircraft)))
print("Total Flights in Input File: {0}".format(len(flights)))
arcpy.AddMessage("Total Flights in Input File: {0}".format(len(flights)))
print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
