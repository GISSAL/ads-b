# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: script3.py
    Author: Shawn Hutchinson
    Description:  Calculates sinuosity and fractal dimension for flight lines
    Date created: 9/30/2021
    Date last modified: 10/1/2021
    Python Version: 3.7
    Source:  https://gis.stackexchange.com/questions/219387/sinuosity-python-script
"""

# Import libraries
import arcpy
import math

# Local variable(s)
inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B.gdb/ADSB_HAVO_20190713_Lines_25Miles_AGL"
sinValue = 0.19

# Set local environments
arcpy.env.overwriteOutput = True
arcpy.env.workspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B.gdb/"

# Add a new field to store sinuosity value
arcpy.management.AddField(inputFile, "Sinuosity", "DOUBLE")
arcpy.management.AddField(inputFile, "Fractal", "DOUBLE")

# Define new functions for sinuosity and fractal dimension

def getSinuosity(shape):
    length = shape.length
    d = math.sqrt((shape.firstPoint.X - shape.lastPoint.X) ** 2 + (shape.firstPoint.Y - shape.lastPoint.Y) ** 2)
    return d/length

def getFractal(shape):
    length = shape.length
    d = math.sqrt((shape.firstPoint.X - shape.lastPoint.X) ** 2 + (shape.firstPoint.Y - shape.lastPoint.Y) ** 2)
    n = length / 100
    return math.log(n) / (math.log(n) + math.log(d/length))

# Apply sinuosity and fractal dimension calculations
arcpy.CalculateField_management(inputFile, "Sinuosity", "getSinuosity(!shape!)", "PYTHON3")
arcpy.CalculateField_management(inputFile, "Fractal", "getFractal(!shape!)", "PYTHON3")

## Find flights with sinuosity less than the threshold value (e.g., 0.19) that is indicative of survey flights
#selFlight = arcpy.SelectLayerByAttribute_management(inputFile, "NEW_SELECTION", '"Sinuosity" <= 0.19')
#print("There are {0} flights with a sinuosity less than the threshold value of {1}.".format(str(len(selFlight)), str(sinValue)))
#
## Remove line feature classes with sinuosity less than the threshold value
#if len(selFlight) > 0:
#    arcpy.DeleteFeatures_management(selFlight)
#else:
#    pass