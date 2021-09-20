# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: script2_0.py
    Author: Shawn Hutchinson
    Description:  Ingests processed ADS-B data and produces screened point and line feature classes
    Date created: 7/20/2021
    Date last modified: 8/3/2021
    Python Version: 3.7
"""

# Import libraries
import arcpy

# Local variable(s)
#inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B_Toolkit_Dev/data/ADSB_HAVO_20190708.csv"
#longitudeField = "Longitude"
#latitudeField = "Latitude"
#altitudeField = "Altitude"
#dateTimeField = "DateTime"
#parkBoundaryFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B_Toolkit_Dev/NPS_ADS_B_Toolkit_Dev.gdb/Boundary_HAVO"
#bufferDistance = "25 Miles"
#inputDEM = "D:/GIS_Research/ResearchProjects/NPS_ADS_B_Toolkit_Dev/NPS_ADS_B_Toolkit_Dev.gdb/DEM_10_Hawaii"
#outputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B_Toolkit_Dev/NPS_ADS_B_Toolkit_Dev.gdb/"
#spatialRef = arcpy.SpatialReference(4326)

# Local variable(s)
inputFile = arcpy.GetParameterAsText(0)
longitudeField = "Longitude"
latitudeField = "Latitude"
altitudeField = "Altitude"
dateTimeField = "DateTime"
parkBoundaryFile = arcpy.GetParameterAsText(1)
bufferDistance = arcpy.GetParameterAsText(2)
inputDEM = arcpy.GetParameterAsText(3)
outputWorkspace = arcpy.GetParameterAsText(4)
spatialRef = arcpy.SpatialReference(4326)

# Set local environments
arcpy.env.overwriteOutput = True
arcpy.env.workspace = outputWorkspace

# Parse park name and output filename from input local variables
outputFile = arcpy.Describe(inputFile).baseName
parkName = outputFile[5:9]

# Create point features
arcpy.management.XYTableToPoint(inputFile, outputFile + "_WayPts", longitudeField, latitudeField, altitudeField, spatialRef)

# Converts time values stored in a string to a date field
arcpy.management.ConvertTimeField(outputFile + "_WayPts", dateTimeField, "yyyy-MM-dd HH:mm:ss", "DateTime2", 'DATE')

# Delete unused fields from new point feature class
arcpy.management.DeleteField(outputFile + "_WayPts", ["Field1", "HexID_X", "HexID_Y", "DateTime"])

# Rename DateTime fields in attribute table
arcpy.management.AlterField(outputFile + "_WayPts", 'DateTime2', dateTimeField, dateTimeField)

# Create a park buffer then remove waypoints outside buffer
arcpy.analysis.Buffer(parkBoundaryFile, "Buffer_" + parkName + "_" + bufferDistance.replace(" ", ""), bufferDistance)

# Screen waypoints by a park buffer
arcpy.analysis.Clip(outputFile + "_WayPts", "Buffer_" + parkName + "_" + bufferDistance.replace(" ", ""), outputFile + "_WayPts_" + bufferDistance.replace(" ", ""))

# Perform AGL calculations and add new attribute field to waypoints
arcpy.sa.ExtractValuesToPoints(outputFile + "_WayPts_" + bufferDistance.replace(" ", ""), inputDEM,  outputFile + "_WayPts_" + bufferDistance.replace(" ", "") + "_AGL")

# Subtract DEM (RASTERVALU) from Altitude to create Altitude_AGL field
arcpy.management.CalculateField(outputFile + "_WayPts_" + bufferDistance.replace(" ", "") + "_AGL", "Altitude_AGL", "!Altitude! - 3.28084 * !RASTERVALU!", "PYTHON3", "", "LONG")
arcpy.management.DeleteField(outputFile + "_WayPts_" + bufferDistance.replace(" ", "") + "_AGL", ["RASTERVALU"])

# Create line feature class from screened waypoints
arcpy.management.PointsToLine(outputFile + "_WayPts_" + bufferDistance.replace(" ", ""), outputFile + "_Lines_" + bufferDistance.replace(" ", "") + "_AGL", 'FlightID')
