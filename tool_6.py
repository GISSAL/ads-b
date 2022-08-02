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
inputFile = arcpy.GetParameterAsText(0)
outputWorkspace = arcpy.GetParameterAsText(1)

# Set local environments
arcpy.env.workspace = outputWorkspace
arcpy.env.overwriteOutput = True

# Fixed local variables
totalWaypoints = 0

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Creating a temporary copy of the merged waypoint input file and removing identical Flight ID's...", 0, 4, 1)
    
    # Create a temporary copy of the merged waypoint file then delete records with identical flight id's
    # Note:  This keeps only the first waypoint for each flight for summarizing when the flight took place
    arcpy.management.Copy(inputFile, inputFile + "_Copy")
    arcpy.management.DeleteIdentical(inputFile + "_Copy", "flight_id")  
    print("Copy of input file created and identical Flight ID's removed.")    
    
    # Convert local DateTime field to text, then parse into HOUR and MONTH fields for later summarization
    arcpy.SetProgressorLabel("Converting recorded DateTime to local time and creating new hour and month fields...")
    arcpy.SetProgressorPosition()
    print("Converting recorded DateTime to local time and creating new hour and month fields...")
    arcpy.management.ConvertTimeField(inputFile + "_Copy", 'TIME', "", "TIME_TEXT", 'TEXT', "yyyy/MM/dd HH:mm:ss")
    arcpy.management.CalculateField(inputFile + "_Copy", "HOUR", "!TIME_TEXT![-8:-6]", 'PYTHON3')
    arcpy.management.CalculateField(inputFile + "_Copy", "MONTH", "!TIME_TEXT![-14:-12]", 'PYTHON3')
    print("Local time, hour, and month fields calculated.")    
    
    print("Calculating flight summaries by hour and month (frequencies and percentages)...") 
    arcpy.SetProgressorLabel("Calculating flight summaries by hour and month (frequencies and percentages)...")
    arcpy.SetProgressorPosition()    
    arcpy.analysis.Frequency(inputFile + "_Copy", "WaypointSummary_HR", "HOUR")
    arcpy.analysis.Frequency(inputFile + "_Copy", "WaypointSummary_MO", "MONTH")      
    with arcpy.da.SearchCursor("WaypointSummary_HR", "FREQUENCY") as cursor:
        for row in cursor:
            totalWaypoints += row[0]
    arcpy.management.AddField("WaypointSummary_HR", "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField("WaypointSummary_MO", "PERCENTAGE", "DOUBLE")    
    with arcpy.da.UpdateCursor("WaypointSummary_HR", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])            
    with arcpy.da.UpdateCursor("WaypointSummary_MO", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])            
    print("Hourly and monthly flight summaries calculated.") 
    
    # Delete copy of temporary merged waypoint file
    arcpy.SetProgressorLabel("Deleting copy of merged waypoint input file...")
    arcpy.SetProgressorPosition()       
    print("Deleting copy of merged waypoint input file...")     
    arcpy.management.Delete(inputFile + "_Copy")
    print("File successfully deleted.") 
  
    # Report final aircraft summaries
    print("Success... Aircraft waypoint hours and months summarized!")
    arcpy.AddMessage("Success... Aircraft waypoint hours and months summarized!")
    print("A total of {0} waypoints were used to generate summary data.".format(str(totalWaypoints)))
    arcpy.AddMessage("A total of {0} waypoints were used to generate summary data.".format(str(totalWaypoints)))
        
    # Reset the progressor
    arcpy.ResetProgressor()
    
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
