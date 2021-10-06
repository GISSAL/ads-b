# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_3.py
    Author: Shawn Hutchinson
    Description:  ArcGIS script tool code that calculates sinuosity and fractal dimension for flight lines
    Date created: 10/1/2021
    Date last modified: 10/1/2021
    Python Version: 3.7
    Source:  https://gis.stackexchange.com/questions/219387/sinuosity-python-script
"""

# Import libraries
import arcpy
import math

# Local variable(s)
inputFile = arcpy.GetParameterAsText(0)
sinValue = arcpy.GetParameterAsText(1)

# Set local environments
arcpy.env.overwriteOutput = True
arcpy.env.workspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B.gdb/"

# Add a new field to store sinuosity value
arcpy.management.AddField(inputFile, "Sinuosity", "DOUBLE")
arcpy.management.AddField(inputFile, "Fractal", "DOUBLE")

# Define new functions for sinuosity and fractal dimension
codeblock1 = """
def getSinuosity(shape):
    length = shape.length
    d = math.sqrt((shape.firstPoint.X - shape.lastPoint.X) ** 2 + (shape.firstPoint.Y - shape.lastPoint.Y) ** 2)
    return d/length"""

codeblock2 = """
def getFractal(shape):
    length = shape.length
    d = math.sqrt((shape.firstPoint.X - shape.lastPoint.X) ** 2 + (shape.firstPoint.Y - shape.lastPoint.Y) ** 2)
    n = length / 100
    return math.log(n) / (math.log(n) + math.log(d/length))"""

# Apply sinuosity and fractal dimension calculations
arcpy.CalculateField_management(inputFile, "Sinuosity", "getSinuosity(!shape!)", "PYTHON3", codeblock1)
arcpy.CalculateField_management(inputFile, "Fractal", "getFractal(!shape!)", "PYTHON3", codeblock2)