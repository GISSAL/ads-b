# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_5.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Generates output tables summarizing waypoint altitudes (both MSL and AGL) by ten user-defined bands.
    Status:  Development
    Date created: 1/24/2022
    Date last modified: 8/2/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
inputFile = arcpy.GetParameterAsText(0)
outputWorkspace = arcpy.GetParameterAsText(1)
alt1 = arcpy.GetParameterAsText(2)
alt2 = arcpy.GetParameterAsText(3)
alt3 = arcpy.GetParameterAsText(4)
alt4 = arcpy.GetParameterAsText(5)
alt5 = arcpy.GetParameterAsText(6)
alt6 = arcpy.GetParameterAsText(7)
alt7 = arcpy.GetParameterAsText(8)
alt8 = arcpy.GetParameterAsText(9)
alt9 = arcpy.GetParameterAsText(10)
alt10 = arcpy.GetParameterAsText(11)

# Set local environments
arcpy.env.workspace = outputWorkspace
arcpy.env.overwriteOutput = True

# Fixed local variables
totalWaypoints = 0
reclassTable =  [[alt1, "1"], [alt2, "2"], [alt3, "3"],  [alt4, "4"],  [alt5, "5"],  [alt6, "6"],  [alt7, "7"],  [alt8, "8"],  [alt9, "9"],  [alt10, "10"]]

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Reclassifying waypoints by AGL and MSL altitude bands...", 0, 3, 1)
    
    # Reclassify merged waypoints
    arcpy.management.ReclassifyField(inputFile, "alt_agl", "MANUAL", "", "", "", reclassTable, "", "alt_agl_MANUAL")
    arcpy.management.ReclassifyField(inputFile, "alt_msl", "MANUAL", "", "", "", reclassTable, "", "alt_msl_MANUAL")   
    print("Reclassification complete.")    
    
    # Summarize waypoint altitudes and write output to two new tables
    arcpy.SetProgressorLabel("Calculating altitude frequencies and percentages...")
    arcpy.SetProgressorPosition()
    arcpy.analysis.Frequency(inputFile, "WaypointSummary_AGL", "alt_agl_MANUAL_RANGE")
    arcpy.analysis.Frequency(inputFile, "WaypointSummary_MSL", "alt_msl_MANUAL_RANGE")   
    with arcpy.da.SearchCursor("WaypointSummary_AGL", "FREQUENCY") as cursor:
        for row in cursor:
            totalWaypoints += row[0]
    arcpy.management.AddField("WaypointSummary_AGL", "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField("WaypointSummary_MSL", "PERCENTAGE", "DOUBLE")
    with arcpy.da.UpdateCursor("WaypointSummary_AGL", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])         
    with arcpy.da.UpdateCursor("WaypointSummary_MSL", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])       
    print("Waypoint frequencies and percentages calculated.") 
    
    # Clean-up original merged waypoint attribute table
    arcpy.SetProgressorLabel("Deleting unneeded fields from original merged waypoint attribute table...")
    arcpy.SetProgressorPosition()
    arcpy.management.DeleteField(inputFile, ["alt_agl_MANUAL", "alt_agl_MANUAL_RANGE", "alt_msl_MANUAL", "alt_msl_MANUAL_RANGE"])
    print("Unneeded fields successfully deleted.")     
    
    # Report final aircraft summaries
    print("Success... Aircraft waypoint altitudes summarized!")
    arcpy.AddMessage("Success... Aircraft waypoint altitudes summarized!")
    print("There were a total of {0} waypoints in the merged waypoint input file.".format(str(totalWaypoints)))
    arcpy.AddMessage("There are were total of {0} waypoints in the merged waypoint input file.".format(str(totalWaypoints)))
       
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

except:
    print("An unexpected error occurred processing the input file {0}".format(inputFile))
    arcpy.AddWarning("An unexpected error occurred processing the input file {0}".format(inputFile))

finally:    
    # Report execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
