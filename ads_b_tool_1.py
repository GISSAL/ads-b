# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: ads_b_tool_1.py
    Author: Shawn Hutchinson
    Credits: Damon Joyce, Shawn Hutchinson, Brian Peterson, Myles Cramer, Davyd Betchkal
    Description:  ArcGIS script tool code that reads raw ADS-B data from the logger, creates unique flights, and generates output CSV for later GIS operations
    Status:  Development
    Date created: 10/6/2021
    Date last modified: 02/26/2024
    Python Version: 3.9.16
"""

# Create custom error class
class HeaderError(Exception):
    pass

# Import libraries
import arcpy, os, pandas as pd, time, numpy as np

# User-specified local variable(s) for ArcGIS script tool
park_name = arcpy.GetParameterAsText(0)
logger_name = arcpy.GetParameterAsText(1)
input_file = arcpy.GetParameterAsText(2)
dur_threshold = arcpy.GetParameterAsText(3)
output_workspace = arcpy.GetParameterAsText(4)

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Reading input file and checking for the required header...", 0, 14, 1)
    
    # Extract the basename of the input TSV file
    base = os.path.basename(input_file)
    
    # Read in ADS-B text file and check for presence of a single text header row
    # How the pandas read_csv function checks for and warns users of bad lines changed at version 1.3.   
    # The initial pandas version check ensures users running ArcGIS 2.x and 3.x can both run the script.
    pd_version = float(pd.__version__[:-2])
    if (pd_version < 1.3):
        data = pd.read_csv(input_file, sep="\t", low_memory=False, error_bad_lines=False, warn_bad_lines=True)
    else:
        data = pd.read_csv(input_file, sep="\t", low_memory=False, on_bad_lines="warn")
    mask = data.iloc[:, 0].isin(["TIME", "timestamp"])
    data = data[~mask]
    header_list = ["TIME", "timestamp"]
    import_header = data.axes[1]
    result = any(elem in import_header for elem in header_list)
    if result:
        pass    
    else:        
        raise HeaderError
    print("Input ADS-B file has the required header.")
    arcpy.AddMessage("Input ADS-B file has the required header.")
    
    # Standardize key field names and remove extra columns collected by the ADS-B data logger
    arcpy.SetProgressorLabel("Standarizing key field names and removing unused fields...")
    arcpy.SetProgressorPosition()
    if "timestamp" in data.columns:
        data = data.rename(columns={"timestamp":"TIME"})
    if "valid_flags" in data.columns:
        data = data.rename(columns={"valid_flags":"validFlags"})
    if "altitude_type" in data.columns:
        data = data.rename(columns={"altitude_type":"altType"})
    if "alt_type" in data.columns:
        data = data.rename(columns={"alt_type":"altType"})
    data.drop(["squawk", "callsign", "emitter_type", "emitterType"], axis=1, inplace=True, errors="ignore")
    print("Key field names standardized and unused fields removed.")
    arcpy.AddMessage("Key field names standardized and unused fields removed.")
    
    # Unpack validFLags data and convert the 2-byte flag field into a list of Boolean values
    arcpy.SetProgressorLabel("Unpacking data in validFlags field and converting to boolean values...")
    arcpy.SetProgressorPosition()
    flags_names = ["valid_BARO", "valid_VERTICAL_VELOCITY", "SIMULATED_REPORT", "valid_IDENT", "valid_CALLSIGN", "valid_VELOCITY", "valid_HEADING", "valid_ALTITUDE", "valid_LATLON"]
    flags = data["validFlags"].apply(lambda t: list(bin(int(t, 16))[2:].zfill(9)[-9:]))
    flags_df = pd.DataFrame(list(flags), columns=flags_names).replace({'0': False, '1': True})
    data = pd.concat([data.drop("validFlags", axis=1), flags_df], axis=1)
    print("Data in validFlags field unpacked and converted to boolean values.")
    arcpy.AddMessage("Data in validFlags field unpacked and converted to boolean values.")
    
    # Keep only those records with valid latlon and altitude values based on validFlags
    arcpy.SetProgressorLabel("Identifying rows with invalid altitudes and lat/long coordinates...")
    arcpy.SetProgressorPosition()
    if data["valid_LATLON"].sum() == len(data.index):
        invalidLatLon = 0
    else:    
        invalidLatLon = round(100 - data["valid_LATLON"].sum() / len(data.index) * 100, 2)
    if data["valid_ALTITUDE"].sum() == len(data.index):
        invalidAltitude = 0
    else:    
        invalidAltitude = round(100 - data["valid_ALTITUDE"].sum() / len(data.index) * 100, 2)
    data.drop(data[data["valid_LATLON"] == "False"].index, inplace = True)
    data.drop(data[data["valid_ALTITUDE"] == "False"].index, inplace = True)
    print("Rows with invalid flags for altitude and lat/lon coordinates removed.")
    arcpy.AddMessage("Rows with invalid flags for altitude and lat/lon coordinates removed.")
    
    # Ensure remaining field values (except TIME) use proper data types
    arcpy.SetProgressorLabel("Formatting field values...")
    arcpy.SetProgressorPosition()
    data.replace('-', np.NaN, inplace=True)
    data.dropna(how="any", axis=0, inplace=True)
    data["ICAO_address"] = data["ICAO_address"].astype(str)
    data["lat"] = data["lat"].astype(int)
    data["lon"] = data["lon"].astype(int)
    data["altitude"] = data["altitude"].astype(int)
    if "altType" in data.columns:
        data["altType"] = data["altType"].astype(int)
        pressureAlts = len(data["altType"] == 0) / len(data) * 100           
    data["heading"] = data["heading"].astype(int)
    data["hor_velocity"] = data["hor_velocity"].astype(int)
    data["ver_velocity"] = data["ver_velocity"].astype(int)
    data["tslc"] = data["tslc"].astype(int)
    
    # Convert Unix-based TIME field to datetime objects in then re-scale selected numeric variable values 
    # Note that the TIME field is controlled by the ADS-B logger which is initialized by local users in local time
    arcpy.SetProgressorLabel("Converting TIME field to datetime objects and re-scaling numeric variables...")
    arcpy.SetProgressorPosition()
    data["TIME"] = pd.to_datetime(data["TIME"], unit = "s")
    data["lat"] = data["lat"] / 1e7
    data["lon"] = data["lon"] / 1e7
    data["altitude"] = data["altitude"] / 1e3
    data["heading"] = data["heading"] / 1e2
    data["hor_velocity"] = data["hor_velocity"] / 1e2
    data["ver_velocity"] = data["ver_velocity"] / 1e2
    data["SITE"] = logger_name
    data["DATE"] = data["TIME"].dt.strftime("%Y%m%d")
    print("ADS-B field data types properly formatted and re-scaled.")
    arcpy.AddMessage("ADS-B field data types properly formatted and re-scaled.")
    
    # Keep only those records with TSLC values of 1 or 2 seconds
    arcpy.SetProgressorLabel("Removing records with TSLC values of 0 and greater than 2 seconds...")
    arcpy.SetProgressorPosition()
    invalidTslc = len(data.query("tslc >= 3 or tslc == 0")) / data.shape[0] * 100
    data.drop(data[data["tslc"] >= 3].index, inplace = True)
    data.drop(data[data["tslc"] == 0].index, inplace = True)
    print("Data screened for valid TSLC values.")
    arcpy.AddMessage("Data screened for valid TSLC values.")

    # Remove lat/lon coordinates that are obviously incorrect
    invalidLat = len(data.query("lat >= 90 or lat <= -90")) / data.shape[0] * 100
    invalidLon = len(data.query("lon >= 180 or lon <= -180")) / data.shape[0] * 100
    data.drop(data[data["lat"] >= 90].index, inplace = True)
    data.drop(data[data["lat"] <= -90].index, inplace = True)
    data.drop(data[data["lon"] >= 180].index, inplace = True)
    data.drop(data[data["lon"] <= -180].index, inplace = True)
    invalidCoords = invalidLatLon + invalidLat + invalidLon
    print("Data screened for additional invalid coordinate values.")
    arcpy.AddMessage("Data screened for additional invalid coordinate values.")

    # Count then delete any duplicate waypoints in a single input file
    duplicateWaypoints = 100 - (len(data.drop_duplicates(subset=["TIME", "ICAO_address", "lat", "lon", "altitude", "heading"])) / len(data) * 100)
    data.drop_duplicates(subset=["TIME", "ICAO_address", "lat", "lon", "altitude", "heading"], keep = 'last', inplace = True)    
    print("Duplicate aircraft waypoints removed.")
    arcpy.AddMessage("Duplicate aircraft waypoints removed.")

    # Sort records by ICAO_address and TIME then reset dataframe index
    arcpy.SetProgressorLabel("Sorting records by ICAO Address and Time...")
    arcpy.SetProgressorPosition()
    data.sort_values(["ICAO_address", "TIME"], inplace = True)
    print(len(data))
    data = data.reset_index(drop=True)
    print("ADS-B records sorted by ICAO Address and Time.")
    arcpy.AddMessage("ADS-B records sorted by ICAO Address and Time.")
    
    # Simplify waypoints by removing rows with sequential values
    preSimplify = len(data)    
    cols = ["ICAO_address", "lat", "lon", "altitude", "heading", "SITE"]
    data = data.loc[(data[cols].shift() != data[cols]).any(axis=1)]
    postSimplify = len(data)
    percentSimplify = ((preSimplify - postSimplify) / preSimplify) * 100
    print("ADS-B records simplified by removing sequential duplicates.")
    arcpy.AddMessage("ADS-B records simplified by removing sequential duplicates.")

    # Drop fields no longer needed
    data = data.drop(columns = ['tslc', 'valid_BARO', 'valid_VERTICAL_VELOCITY', 'SIMULATED_REPORT', 'valid_IDENT', 'valid_CALLSIGN', 'valid_VELOCITY', 'valid_HEADING', 'valid_ALTITUDE', 'valid_LATLON'])
    
    # Calculate time difference between sequential waypoints for each aircraft
    arcpy.SetProgressorLabel("Calculating time difference between waypoints for each aircraft...")
    arcpy.SetProgressorPosition()
    data["dur_secs"] = data.groupby("ICAO_address")["TIME"].diff().dt.total_seconds()
    data["dur_secs"] = data["dur_secs"].fillna(0)
    
    # Use threshold waypoint duration value to identify separate flights by an aircraft then sum the number of "true" conditions to assign unique ID's
    arcpy.SetProgressorLabel("Identifying and creating labels for separate flights by the same aircraft...")
    arcpy.SetProgressorPosition()
    data['diff_flight'] = data['dur_secs'] >= int(dur_threshold)  
    data['cumsum'] = data.groupby('ICAO_address')['diff_flight'].cumsum()
    data['flight_id'] = data['ICAO_address'] + "_" + data['cumsum'].astype(str)  + "_" + data['DATE']   
    print("Separate flights by same aircraft identified.")
    arcpy.AddMessage("Separate flights by same aircraft identified.") 

    # Remove records where there is only one recorded waypoint for an aircraft and fields that are no longer needed 
    arcpy.SetProgressorLabel("Removing aircraft records with a single waypoint and unneeded attribute fields...")
    arcpy.SetProgressorPosition()
    data = data[data.groupby("flight_id").flight_id.transform(len) > 1]
    data = data.drop(columns = ['dur_secs', 'diff_flight', 'cumsum'])
    print("Flights with a single waypoint deleted and unneeded attribute fields removed.")
    arcpy.AddMessage("Flights with a single waypoint deleted and unneeded attribute fields removed.") 
    
    # Write output file in CSV format based on the TSV input file name
    arcpy.SetProgressorLabel("Writing the output CSV file...")
    arcpy.SetProgressorPosition()
    data.to_csv(output_workspace + "\ADSB_" + park_name + "_" + logger_name + "_" + os.path.splitext(base)[0] + ".csv")
    print("Success... ADS-B data cleaned and formatted output file created!")
    arcpy.AddMessage("Success... ADS-B data cleaned and formatted output file created!")
    
    # Create variables for use in the final summary report available in the script tool message window
    aircraft = data["ICAO_address"].unique()
    flights = data["flight_id"].unique()
    
    # Record end time of operation
    end = time.time()
    
    # Report aircraft and flight summary information in messages for the user
    print("Percent of original waypoints eliminated due to TSLC: {0}".format(str(round(invalidTslc, 2))))
    arcpy.AddMessage("Percent of original waypoints eliminated due to TSLC: {0}".format(str(round(invalidTslc,2))))
    print("Percent duplicate waypoints: {0}".format(str(round(duplicateWaypoints,2))))
    arcpy.AddMessage("Percent duplicate waypoints: {0}".format(str(round(duplicateWaypoints,2))))
    print("Percent waypoints with invalid altitudes: {0}".format(str(invalidAltitude)))
    arcpy.AddMessage("Percent waypoints with invalid altitudes: {0}".format(str(invalidAltitude)))
    print("Duplicate sequential waypoints deleted: {0}".format(str(round(percentSimplify,2))))
    arcpy.AddMessage("Duplicate sequential waypoints deleted: {0}".format(str(round(percentSimplify,2))))
    print("Percent waypoints with invalid x,y coordinates: {0}".format(str(round(invalidCoords, 2))))
    arcpy.AddMessage("Percent waypoints with invalid x,y coordinates: {0}".format(str(round(invalidCoords, 2))))
    if "pressureAlts" in locals():
        print("Percent waypoints with pressure altitute estimates: {0}".format(str(round(pressureAlts, 2))))
        arcpy.AddMessage("Percent waypoints with pressure altitudes: {0}".format(str(round(pressureAlts, 2))))
    else:
        pass
    print("Total flights in input file: {0}".format(len(flights)))
    arcpy.AddMessage("Total flights in input file: {0}".format(len(flights)))
    print("Total unique aircraft in input file: {0}".format(len(aircraft)))
    arcpy.AddMessage("Total unique aircraft in input file: {0}".format(len(aircraft)))

    # Reset the progressor
    arcpy.ResetProgressor()

except HeaderError:
    print("Input file does not have the required text header...processing cannot proceed!")
    arcpy.AddWarning("The input file {0} does not have the required text header...processing cannot proceed!".format(base))
    
except:
    print("An unexpected error occurred processing the input file {0}".format(base))
    arcpy.AddWarning("An unexpected error occurred processing the input file {0}".format(base))
    
finally:    
    # Report script tool execution time if an exception is encountered
    if "end" in locals():
        pass
    else:
        end = time.time()
        print("Total execution time (secs) = {0}".format(str(round(end - start, 3))))    
        arcpy.AddMessage("Total execution time (secs) = {0}".format(str(round(end - start, 3))))
