# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: grsm_script_2.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Ingests processed ADS-B data and produces point and line feature classes
    Status:  Development
    Date created: 10/7/2021
    Date last modified: 12/02/2021
    Python Version: 3.7
"""
# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
inputFile = arcpy.GetParameterAsText(0)
parkBoundaryFile = arcpy.GetParameterAsText(1)
bufferDistance = arcpy.GetParameterAsText(2)
inputDEM = arcpy.GetParameterAsText(3)
outputWorkspace = arcpy.GetParameterAsText(4)

# User-specified local variable(s) for stand-alone Python script
#inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/Outputs/ADSB_GRSM_20190925.csv"
#parkBoundaryFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/Boundary_GRSM"
#bufferDistance = "25 Miles"
#inputDEM = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/DEM_10_GRSM"
#outputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb"

# Fixed local variable(s)
spatialRef = arcpy.SpatialReference(4269)

# Set local environments
arcpy.env.workspace = outputWorkspace
arcpy.env.overwriteOutput = True

try:
    
    # Start timer
    start = time.time()
    
    if arcpy.CheckExtension("Spatial") == "Available":
        
        # Parse park name and output filename from input local variables
        outputFile = arcpy.Describe(inputFile).baseName
        parkName = outputFile[5:9]
        print("Reading in ADS-B waypoint data...")
        arcpy.AddMessage("Reading in ADS-B waypoint data...")
        
        # Create point features
        arcpy.management.XYTableToPoint(inputFile, "temp1", "lon", "lat", "altitude", spatialRef)
        print("Point feature class created from ADS-B input file...")
        arcpy.AddMessage("Point feature class created from ADS-B input file...")
        
        # Delete identical waypoints based on ICAO_address, lat, and lon
        arcpy.management.DeleteIdentical("temp1", ["ICAO_address", "TIME", "lat", "lon"])
        print("Identical waypoints removed...")
        arcpy.AddMessage("Identical waypoints removed...")
        
        # Create a park buffer then remove waypoints outside buffer
        arcpy.analysis.Buffer(parkBoundaryFile, "Buffer_" + parkName + "_" + bufferDistance.replace(" ", ""), bufferDistance)
        
        # Screen waypoints by a park buffer
        arcpy.analysis.Clip("temp1", "Buffer_" + parkName + "_" + bufferDistance.replace(" ", ""), "temp2")
        print("Park buffer generated and points outside buffer removed...")
        arcpy.AddMessage("Park buffer generated and waypoints outside buffer removed...")
        
        # Perform AGL calculations and add new attribute field to waypoints
        arcpy.sa.ExtractValuesToPoints("temp2", inputDEM,  outputFile + "_Points_" + bufferDistance.replace(" ", ""))
        
        # Subtract DEM (RASTERVALU) from Altitude to create Altitude_AGL field
        arcpy.management.CalculateField(outputFile + "_Points_" + bufferDistance.replace(" ", ""), "alt_agl", "!altitude! - !RASTERVALU!", "PYTHON3", "", "LONG")
        arcpy.management.DeleteField(outputFile + "_Points_" + bufferDistance.replace(" ", ""), ["RASTERVALU"])
        
        # Recalculate alt_agl to convert from meters to feet
        arcpy.management.CalculateField(outputFile + "_Points_" + bufferDistance.replace(" ", ""), "alt_agl", "!alt_agl! * 3.28084", "PYTHON3", "", "LONG")
        print("Aircraft altitude above ground level (AGL) calculated...")
        arcpy.AddMessage("Aircraft altitude above ground level (AGL) calculated...")
        
        # Create line feature class from screened waypoints
        arcpy.management.PointsToLine(outputFile + "_Points_" + bufferDistance.replace(" ", ""), "temp3", "flight_id", "TIME")
        
        # Retain only line features with > 0 length (0 length indicates 2 input waypoints with same x- and y-coordinate values)
        selRecs = arcpy.management.SelectLayerByAttribute("temp3", "NEW_SELECTION", "Shape_Length > 0")
        arcpy.management.CopyFeatures(selRecs, outputFile + "_Lines_" + bufferDistance.replace(" ", ""))
        
        # Add a new field to store HexID, retrieve values from FlightID, then delete FlightID
        arcpy.management.AddField(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), "ICAO_address", "TEXT")
        arcpy.CalculateField_management(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), "ICAO_address", "!flight_id![:6]", "PYTHON3")
        arcpy.management.DeleteField(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), "flight_id")
        print("Line feature class created from ADS-B waypoint data...")
        arcpy.AddMessage("Line feature class created from ADS-B waypoint data...")
                
        # Delete files no longer needed
        delList = arcpy.ListFeatureClasses("temp*")
        for i in delList:
            arcpy.management.Delete(i)
        print("Intermediate data removed from workspace...")
        arcpy.AddMessage("Intermediate data removed from workspace...")

    else:
        arcpy.AddMessage("An ArcGIS SPatial Analyst extension is required!  The current status of this extension is {0}.".format(arcpy.CheckExtension("Spatial")))
        
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report aircraft and flight summaries and execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))