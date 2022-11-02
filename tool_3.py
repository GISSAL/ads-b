# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_3.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson, Myles Cramer
    Description:  Merges daily aircraft waypoint and flightlines feature classes into single feature classes for a desired time interval.
    Status:  Development
    Date created: 12/15/2021
    Date last modified: 11/2/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
inputWorkspace = arcpy.GetParameterAsText(0)
outputPoints = arcpy.GetParameterAsText(1)
outputLines = arcpy.GetParameterAsText(2)

# Set local environments
arcpy.env.workspace = inputWorkspace
arcpy.env.overwriteOutput = True

# Fixed local variables
pointList = []
lineList = []

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Creating a list of daily aircraft waypoint and flightline files...", 0, 4, 1)
       
    # Search input workspace and identify aircraft waypoint point and flight line feature classes
    for fc in arcpy.ListFeatureClasses():
        desc = arcpy.Describe(fc)
        if desc.shapeType == "Point":
            pointList.append(fc)
        if desc.shapeType == "Polyline":
            lineList.append(fc)     
            
    # Merge point feature classes into a single file without duplicates
    arcpy.SetProgressorLabel("Merging waypoint feature classes into a single point feature class...")
    arcpy.SetProgressorPosition()
    if len(pointList) > 0:
        desc = arcpy.Describe(pointList[0])
        parkName = desc.baseName[5:9]       
        arcpy.management.Merge(pointList, outputPoints)
        count1 = arcpy.management.GetCount(outputPoints)
        arcpy.management.ConvertTimeField(outputPoints, 'TIME', "", 'DATE', 'TEXT', 'yyyyMMdd')
        arcpy.management.DeleteIdentical(outputPoints, ['flight_id', 'lat', 'lon', 'DATE'])
        count2 = arcpy.management.GetCount(outputPoints)
        count3 = int(str(count1)) - int(str(count2))
        arcpy.management.DeleteField(outputPoints, "DATE")        
        print("A total of {0} aircraft waypoints were found in the input point feature classes.".format(str(count1)))        
        arcpy.AddMessage("A total of {0} aircraft waypoints were found in the input point feature classes.".format(str(count1)))
        print("A total of {0} duplicate aircraft waypoints were removed from the input files.".format(str(count3)))
        arcpy.AddMessage("A total of {0} duplicate aircraft waypoints were removed from the input files.".format(str(count3)))
        print("A total of {0} unique aircraft waypoints were written to the merged point feature class.".format(str(count2)))        
        arcpy.AddMessage("A total of {0} unique aircraft waypoints were written to the merged point feature class.".format(str(count2)))        
    else:
        print("There are no waypoint files in the workspace {0}!")
        arcpy.AddWarning("There are no waypoint files in the workspace!")
        pass

    # Merge line feature classes into a single file
    arcpy.SetProgressorLabel("Merging flightline feature classes into a single line feature class...")
    arcpy.SetProgressorPosition()
    if len(lineList) > 0:
        desc = arcpy.Describe(lineList[0])
        parkName = desc.baseName[5:9]
        arcpy.management.Merge(lineList, outputLines)
        count4 = arcpy.management.GetCount(outputLines)
        print("A total of {0} unique aircraft flightlines were written to the merged line feature class.".format(str(count4)))        
        arcpy.AddMessage("A total of {0} unique aircraft flightlines were written to the merged line feature class.".format(str(count4)))           
    else:
        print("There are no flightline files in the workspace!")
        arcpy.AddWarning("There are no flightline files in the workspace!")
        pass

    # Report final aircraft summaries
    arcpy.SetProgressorLabel("Preparing aircraft and flight summary information...")
    arcpy.SetProgressorPosition()
    print("Success... Aircraft feature classes merged into a single file!")
    arcpy.AddMessage("Success... Aircraft feature classes merged into a single file!")
    print("A total of {0} point feature classes were merged.".format(str(len(pointList))))
    arcpy.AddMessage("A total of {0} point feature classes were merged.".format(str(len(pointList))))
    print("A total of {0} line feature classes were merged.".format(str(len(lineList))))
    arcpy.AddMessage("A total of {0} line feature classes were merged.".format(str(len(lineList))))

    # Reset the progressor
    arcpy.ResetProgressor()

except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:
    # Report script tool execution time
    end = time.time()    
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
