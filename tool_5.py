# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_5.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Calculate waypoint frequencies and percentages by altitude bands.
    Status:  Development
    Date created: 1/24/2022
    Date last modified: 6/17/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, os, time

# User-specified local variable(s) for ArcGIS script tool
inputFile = arcpy.GetParameterAsText(0)
outputWorkspace = arcpy.GetParameterAsText(1)

# Set local environments
arcpy.env.overwriteOutput = True

# Fixed local variables
totalWaypoints = 0
agl_reclassTable =  [[500, "1"], [1000, "2"], [1500, "3"],  [2000, "4"],  [2500, "5"],  [3000, "6"],  [3500, "7"],  [4000, "8"],  [4500, "9"],  [60000, "10"]]
msl_reclassTable =  [[1000, "1"], [1500, "2"], [2000, "3"],  [2500, "4"],  [3000, "5"],  [3500, "6"],  [4000, "7"],  [4500, "8"],  [5000, "9"],  [60000, "10"]]

try:
    
    # Start timer
    start = time.time()
    
    # Reclassify merged waypoints into 500 m AGL and MSL increments
    print("Reclassifying waypoints by AGL and MSL altitude bands...")
    arcpy.AddMessage("Reclassifying waypoints by AGL and MSL altitude bands...")
    arcpy.management.ReclassifyField(inputFile, "alt_agl", "MANUAL", None, None, "ONE", agl_reclassTable, "", "alt_agl_MANUAL")
    arcpy.management.ReclassifyField(inputFile, "alt_msl", "MANUAL", None, None, "ONE", msl_reclassTable, "", "alt_msl_MANUAL")   
    print("Reclassification complete.")
    arcpy.AddMessage("Reclassification complete.")
    
    # Summarize waypoint altitudes in two new tables
    print("Calculating frequencies and percentages...") 
    arcpy.AddMessage("Calculating frequencies and percentages...")
    arcpy.analysis.Frequency(inputFile, os.path.join(outputWorkspace + "/WaypointSummary_AGL"), "alt_agl_MANUAL")
    arcpy.analysis.Frequency(inputFile, os.path.join(outputWorkspace + "/WaypointSummary_MSL"), "alt_msl_MANUAL")   
    with arcpy.da.SearchCursor(os.path.join(outputWorkspace + "/WaypointSummary_AGL"), "FREQUENCY") as cursor:
        for row in cursor:
            totalWaypoints += row[0]
    arcpy.management.AddField(os.path.join(outputWorkspace + "/WaypointSummary_AGL"), "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField(os.path.join(outputWorkspace + "/WaypointSummary_MSL"), "PERCENTAGE", "DOUBLE")
    with arcpy.da.UpdateCursor(os.path.join(outputWorkspace + "/WaypointSummary_AGL"), ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, (frequency / totalWaypoints) * 100])
    with arcpy.da.UpdateCursor(os.path.join(outputWorkspace + "/WaypointSummary_MSL"), ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, (frequency / totalWaypoints) * 100])            
    print("Waypoint frequencies and percentages calculated.") 
    arcpy.AddMessage("Waypoint frequencies and percentages calculated.")
            
    # Clean-up original merged waypoint attribute table
    print("Deleting unneeded fields from original merged waypoint attribute table...") 
    arcpy.AddMessage("Deleting unneeded fields from original merged waypoint attribute table...")
    arcpy.management.DeleteField(inputFile, ["alt_agl_MANUAL", "alt_agl_MANUAL_RANGE", "alt_msl_MANUAL", "alt_msl_MANUAL_RANGE"])
    print("Unneeded fields successfully deleted.") 
    arcpy.AddMessage("Unneeded fields successfully deleted.")
       
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
    print("There are a total of {0} waypoints in the merged waypoint input file.".format(str(totalWaypoints)))
    arcpy.AddMessage("There are a total of {0} waypoints in the merged waypoint input file.".format(str(totalWaypoints)))
