# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_5.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Generates output tables summarizing waypoint altitudes (both MSL and AGL) by ten user-defined bands.
    Status:  Development
    Date created: 1/24/2022
    Date last modified: 11/4/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
parkName = arcpy.GetParameterAsText(0)
inputWaypoints = arcpy.GetParameterAsText(1)
parkBoundaryFile = arcpy.GetParameterAsText(2)
bufferDistance = arcpy.GetParameterAsText(3)
alt1 = arcpy.GetParameterAsText(4)
alt2 = arcpy.GetParameterAsText(5)
alt3 = arcpy.GetParameterAsText(6)
alt4 = arcpy.GetParameterAsText(7)
alt5 = arcpy.GetParameterAsText(8)
alt6 = arcpy.GetParameterAsText(9)
alt7 = arcpy.GetParameterAsText(10)
alt8 = arcpy.GetParameterAsText(11)
alt9 = arcpy.GetParameterAsText(12)
alt10 = arcpy.GetParameterAsText(13)

# Set local environments
arcpy.env.workspace = arcpy.Describe(inputWaypoints).path
arcpy.env.overwriteOutput = True

# Fixed local variables
totalWaypoints = 0
reclassTable =  [[alt1, "1"], [alt2, "2"], [alt3, "3"],  [alt4, "4"],  [alt5, "5"],  [alt6, "6"],  [alt7, "7"],  [alt8, "8"],  [alt9, "9"],  [alt10, "10"]]

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Creating the buffer and clipping screened waypoints...", 0, 3, 1)
    
    # NEW - Create buffer polygon around park boundary based on user-defined distance, then clip the inputFile
    arcpy.analysis.Buffer(parkBoundaryFile, "temp1", bufferDistance)
    arcpy.analysis.Clip(inputWaypoints,  "temp1", "temp2") 
    print("Buffer created and waypoints clipped.")    
    arcpy.AddMessage("Buffer created and waypoints clipped.")    
    
    # Reclassify merged waypoints
    arcpy.SetProgressorLabel("Reclassifying waypoints by AGL and MSL altitude bands...")
    arcpy.SetProgressorPosition()
    arcpy.management.ReclassifyField("temp2", "alt_agl", "MANUAL", "", "", "", reclassTable, "", "alt_agl_MANUAL")
    arcpy.management.ReclassifyField("temp2", "alt_msl", "MANUAL", "", "", "", reclassTable, "", "alt_msl_MANUAL")   
    print("Reclassification complete.")    
    arcpy.AddMessage("Reclassification complete.")
    
    # Summarize waypoint altitudes and write output to two new tables
    arcpy.SetProgressorLabel("Calculating altitude frequencies and percentages...")
    arcpy.SetProgressorPosition()
    arcpy.analysis.Frequency("temp2", parkName + "_" + "WaypointSummary_AGL", "alt_agl_MANUAL_RANGE")
    arcpy.analysis.Frequency("temp2", parkName + "_" + "WaypointSummary_MSL", "alt_msl_MANUAL_RANGE")   
    with arcpy.da.SearchCursor(parkName + "_" + "WaypointSummary_AGL", "FREQUENCY") as cursor:
        for row in cursor:
            totalWaypoints += row[0]
    arcpy.management.AddField(parkName + "_" + "WaypointSummary_AGL", "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField(parkName + "_" + "WaypointSummary_MSL", "PERCENTAGE", "DOUBLE")
    with arcpy.da.UpdateCursor(parkName + "_" + "WaypointSummary_AGL", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])                      
    with arcpy.da.UpdateCursor(parkName + "_" + "WaypointSummary_MSL", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])                        
    print("Waypoint frequencies and percentages calculated.") 
    arcpy.AddMessage("Waypoint frequencies and percentages calculated.")
          
    # Report final aircraft summaries
    print("Success... Aircraft waypoint altitudes summarized!")
    arcpy.AddMessage("Success... Aircraft waypoint altitudes summarized!")
    print("A total of {0} waypoints were used to generate the summary data.".format(str(totalWaypoints)))
    arcpy.AddMessage("A total of {0} waypoints were used to generate the summary data.".format(str(totalWaypoints)))
       
    # Reset the progressor
    arcpy.ResetProgressor()
    
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddError("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

except:
    print("An unexpected error occurred processing the input file {0}".format(inputWaypoints))
    arcpy.AddWarning("An unexpected error occurred processing the input file {0}".format(inputWaypoints))

finally:    
    # Delete files no longer needed
    delList = arcpy.ListFeatureClasses("temp*")
    for i in delList:
        arcpy.management.Delete(i)
        
    # Report execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
