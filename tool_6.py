# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_6.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Generates output tables summarizing waypoint frequencies by hour and month.
    Status:  Development
    Date created: 1/24/2022
    Date last modified: 8/2/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
parkName = arcpy.GetParameterAsText(0)
parkBoundaryFile = arcpy.GetParameterAsText(2)
inputWaypoints = arcpy.GetParameterAsText(1)
bufferDistance = arcpy.GetParameterAsText(3)

# Set local environments
arcpy.env.workspace = arcpy.Describe(inputWaypoints).path
arcpy.env.overwriteOutput = True

# Fixed local variables
totalWaypoints = 0

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Creating the buffer and clipping screened waypoints..", 0, 4, 1)
    
    # Create buffer polygon around park boundary based on user-defined distance, then clips the inputWaypoits
    arcpy.analysis.Buffer(parkBoundaryFile, "temp1", bufferDistance)
    arcpy.analysis.Clip(inputWaypoints,  "temp1", "temp2") 
    print("Buffer created and waypoints clipped.")    
    arcpy.AddMessage("Buffer created and waypoints clipped.")    
    
    # Create a temporary copy of the merged waypoint file then delete records with identical flight id's
    # Note:  This keeps only the first waypoint for each flight for summarizing when the flight took place
    arcpy.SetProgressorLabel("Removing identical Flight ID's from clipped waypoints...")
    arcpy.SetProgressorPosition()
    arcpy.management.DeleteIdentical("temp2", "flight_id")  
    print("Identical Flight ID's removed.")    
    arcpy.AddMessage("Identical Flight ID's removed.")    
   
    # Convert local DateTime field to text, then parse into HOUR and MONTH fields for later summarization
    arcpy.SetProgressorLabel("Converting DateTime to local time and creating new hour and month fields...")
    arcpy.SetProgressorPosition()
    print("Converting DateTime to local time and creating new hour and month fields...")
    arcpy.management.ConvertTimeField("temp2", 'TIME', "", "TIME_TEXT", 'TEXT', "yyyy/MM/dd HH:mm:ss")
    arcpy.management.CalculateField("temp2", "HOUR", "!TIME_TEXT![-8:-6]", 'PYTHON3')
    arcpy.management.CalculateField("temp2", "MONTH", "!TIME_TEXT![-14:-12]", 'PYTHON3')
    print("Local time, hour, and month fields calculated.")    
    arcpy.AddMessage("Local time, hour, and month fields calculated.")    
    
    # Calculate frequencies and percentages
    arcpy.SetProgressorLabel("Calculating hour and month frequencies and percentages...")
    arcpy.SetProgressorPosition()    
    arcpy.analysis.Frequency("temp2", parkName + "_" + "WaypointSummary_HR", "HOUR")
    arcpy.analysis.Frequency("temp2", parkName + "_" + "WaypointSummary_MO", "MONTH")      
    with arcpy.da.SearchCursor(parkName + "_" + "WaypointSummary_HR", "FREQUENCY") as cursor:
        for row in cursor:
            totalWaypoints += row[0]
    arcpy.management.AddField(parkName + "_" + "WaypointSummary_HR", "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField(parkName + "_" + "WaypointSummary_MO", "PERCENTAGE", "DOUBLE")    
    with arcpy.da.UpdateCursor(parkName + "_" + "WaypointSummary_HR", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])            
    with arcpy.da.UpdateCursor(parkName + "_" + "WaypointSummary_MO", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])            
    print("Hourly and monthly flight summaries calculated.") 
    arcpy.AddMessage("Hourly and monthly flight summaries calculated.") 
     
    # Report final aircraft summaries
    print("Success... Aircraft waypoint hours and months summarized!")
    arcpy.AddMessage("Success... Aircraft waypoint hours and months summarized!")
    print("A total of {0} waypoints were used to generate summary data.".format(str(totalWaypoints)))
    arcpy.AddMessage("A total of {0} waypoints were used to generate summary data.".format(str(totalWaypoints)))
        
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
