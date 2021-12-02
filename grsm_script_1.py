# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: grsm_script_1.py
    Author: Shawn Hutchinson
    Credits: Damon Joyce, Davyd Betchkal, Shawn Hutchinson, Brian Peterson
    Description:  ArcGIS script tool code that reads raw ADS-B data from the logger, creates "flights", and prepares new input file for later GIS operations
    Status:  Development
    Date created: 10/6/2021
    Date last modified: 12/02/2021
    Python Version: 3.7
"""

# Import libraries
import arcpy, time, pandas as pd

## User-specified local variable(s) for ArcGIS script tool
park_name = arcpy.GetParameterAsText(0)
input_file = arcpy.GetParameterAsText(1)
input_file_date = arcpy.GetParameterAsText(2)
output_workspace = arcpy.GetParameterAsText(3)
dur_threshold = arcpy.GetParameterAsText(4)

# User-specified local variable(s) for stand-alone Python script
#park_name = "GRSM"
#input_file = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/SampleData/GRSM/COVEMTN/20190925.tsv"
#input_file_date = "20190925"
#output_workspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/Outputs/"
#dur_threshold = 900

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

# Convert Unix timestamp to datetime objects in UTC and re-scale select int values 
data["TIME"] = pd.to_datetime(data["TIME"], unit = "s")
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

# Use threshold waypoint duration value to identify separate flights by aircraft, then sum the number of "true" conditions to assign unique ID
data['diff_flight'] = data['dur_secs'] >= 900
data['cumsum'] = data.groupby('ICAO_address')['diff_flight'].cumsum()
data['flight_id'] = data['ICAO_address'] + "_" + data['cumsum'].astype(str)    
print("Identifying separate flights by same aircraft...")
arcpy.AddMessage("Identifying separate flights by same aircraft...")

# Remove records where there is only one recorded waypoint
data = data[data.groupby("flight_id").flight_id.transform(len) > 1]

# Remove fields that are no longer needed
data = data.drop(columns = ['tslc', 'dur_secs', 'diff_flight', 'cumsum'])

# Write output file in CSV format
data.to_csv(output_workspace + "\ADSB_" + park_name + "_" + input_file_date + ".csv")
print("Success... ADS-B data cleaned and formatted output file created.")
arcpy.AddMessage("Success... ADS-B data cleaned and formatted output file created.")

# Report QA/QC data, aircraft and flight summaries, and execution time
print("Percent of original waypoints eliminated by TSLC: {0}".format(str(round(invalidTslc, 2))))
arcpy.AddMessage("Percent of original waypoints eliminated by TSLC: {0}".format(str(round(invalidTslc,2))))
invalidVelocities = round(data["valid_VELOCITY"].value_counts(normalize=True)[0] * 100, 2)
invalidHeadings = round(data["valid_HEADING"].value_counts(normalize=True)[0] * 100, 2)
invalidAltitudes = round(data["valid_ALTITUDE"].value_counts(normalize=True)[0] * 100, 2)
invalidLatLon = round(data["valid_LATLON"].value_counts(normalize=True)[0] * 100, 2)
aircraft = data["ICAO_address"].unique()
flights = data["flight_id"].unique()
end = time.time()
print("Percent of remaining waypoints with invalid horizontal velocities: {0}".format(str(invalidVelocities)))
arcpy.AddMessage("Percent of remaining waypoints with invalid horizontal velocities: {0}".format(str(invalidVelocities)))
print("Percent of remaining waypoints with invalid headings: {0}".format(str(invalidHeadings)))
arcpy.AddMessage("Percent of remaining waypoints with invalid headings: {0}".format(str(invalidHeadings)))
print("Percent of remaining waypoints with invalid altitudes: {0}".format(str(invalidAltitudes)))
arcpy.AddMessage("Percent of remaining waypoints with invalid altitudes: {0}".format(str(invalidAltitudes)))
print("Percent of remaining waypoints with invalid x,y coordinates: {0}".format(str(invalidLatLon)))
arcpy.AddMessage("Percent of remaining waypoints with invalid x,y coordinates: {0}".format(str(invalidLatLon)))
print("Total Unique Aircraft in Input File: {0}".format(len(aircraft)))
arcpy.AddMessage("Total Unique Aircraft in Input File: {0}".format(len(aircraft)))
print("Total Flights in Input File: {0}".format(len(flights)))
arcpy.AddMessage("Total Flights in Input File: {0}".format(len(flights)))
print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))