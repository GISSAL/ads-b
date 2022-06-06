# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_3.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Combines daily ADS-B files into mergeed waypoints and flightlines
    Status:  Development
    Date created: 12/15/2021
    Date last modified: 2/23/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, os, time

# User-specified local variable(s) for ArcGIS script tool
inputWorkspace = arcpy.GetParameterAsText(0)
parkBoundaryFile = arcpy.GetParameterAsText(1)
outputWorkspace = arcpy.GetParameterAsText(2)
outputPoints = arcpy.GetParameterAsText(3)
outputLines = arcpy.GetParameterAsText(4)

# User-specified local variable(s) for stand-alone Python script
#inputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb"
#parkBoundaryFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/Boundary_GRSM"
#outputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb"
#outputPoints = "MergedWaypoints"
#outputLines = "MergedFlightlines"

# Set local environments
arcpy.env.workspace = inputWorkspace
arcpy.env.overwriteOutput = True

# Fixed local variables
pointList = []
lineList = []

try:
    
    # Start timer
    start = time.time()
       
    # Search input workspace and identify aircraft waypoint point and flight line feature classes
    print("Creating a list of daily aircraft waypoint and flightline files...")
    arcpy.AddMessage("Creating a list of daily aircraft waypoint and flightline files...")
    for fc in arcpy.ListFeatureClasses():
        desc = arcpy.Describe(fc)
        if desc.shapeType == "Point":
            pointList.append(fc)
        if desc.shapeType == "Polyline":
            lineList.append(fc)     
            
    # Merge point and line feature classes into single files and filter by horizontal and vertical buffers
    if len(pointList) > 0:
        print("There are {0} point feature classes to be merged...".format(str(len(pointList))))
        arcpy.AddMessage("There are {0} point feature classes to be merged...".format(str(len(pointList))))
        desc = arcpy.Describe(pointList[0])
        parkName = desc.baseName[5:9]
        arcpy.management.Merge(pointList, os.path.join(outputWorkspace, outputPoints))
        count1 = arcpy.management.GetCount(os.path.join(outputWorkspace, outputPoints))
        print("There are a total of {0} aircraft waypoints in the input point feature classes.".format(str(count1)))
        arcpy.AddMessage("There are a total of {0} aircraft waypoints in the input point feature classes.".format(str(count1)))
        arcpy.management.ConvertTimeField(os.path.join(outputWorkspace, outputPoints), 'TIME', "", 'DATE', 'TEXT', 'yyyyMMdd')
        arcpy.management.DeleteIdentical(os.path.join(outputWorkspace, outputPoints), ['flight_id', 'lat', 'lon', 'DATE'])
        count2 = arcpy.management.GetCount(os.path.join(outputWorkspace, outputPoints))
        count3 = int(str(count1)) - int(str(count2))
        print("A total of {0} duplicate aircraft waypoints were removed leaving {1} total waypoints in the merged waypoint feature class.".format(str(count3), str(count2)))
        arcpy.AddMessage("A total of {0} duplicate aircraft waypoints were removed leaving {1} total waypoints in the merged waypoint feature class.".format(str(count3), str(count2)))
        arcpy.management.DeleteField(os.path.join(outputWorkspace, outputPoints), "DATE")        
 
    if len(lineList) > 0:
        print("There are {0} line feature classes to be merged...".format(str(len(lineList))))
        arcpy.AddMessage("There are {0} line feature classes to be merged...".format(str(len(lineList))))
        desc = arcpy.Describe(lineList[0])
        parkName = desc.baseName[5:9]
        arcpy.management.Merge(lineList, os.path.join(outputWorkspace, outputLines))
        count4 = arcpy.management.GetCount(os.path.join(outputWorkspace, outputLines))
        print("There are {0} total aircraft flights in the merged flightline feature class.".format(str(count4))) 
        arcpy.AddMessage("There are {0} total aircraft flights in the merged flightline feature class.".format(str(count4)))
    else:
        print("There are no waypoints or flight lines in the workspace.")
        arcpy.AddMessage("There are no waypoints or flight lines in the workspace.")
       
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report aircraft and flight summaries and execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
