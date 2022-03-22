# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_6.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Calculate flight summaries by hour and month using waypoints.
    Status:  Development
    Date created: 1/24/2022
    Date last modified: 2/9/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
inputFile = arcpy.GetParameterAsText(0)
outputWorkspace = arcpy.GetParameterAsText(1)
outputTableNameHour = arcpy.GetParameterAsText(2)
outputTableNameMonth = arcpy.GetParameterAsText(3)

# User-specified local variable(s) for stand-alone Python script
#inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/MergedWaypoints"
#outputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb"
#outputTableNameHour = "FlightSummary_HR"
#outputTableNameMonth = "FlightSummary_MO"

# Set local environments
arcpy.env.workspace = outputWorkspace
arcpy.env.overwriteOutput = True

# Fixed local variables
totalFlights = 0

try:
    
    # Start timer
    start = time.time()
    
    # Create a temporary copy of the merged waypoint file then delete records with identical flight id's
    # Note:  This keeps only the first waypoint for each flight for summarizing when the flight took place
    print("Creating a temporary copy of the merged waypoint input file and removing identical Flight ID's...")
    arcpy.AddMessage("Creating a temporary copy of the merged waypoint input file and removing identical Flight ID's...")    
    arcpy.management.Copy(inputFile, inputFile + "_Copy")
    arcpy.management.DeleteIdentical(inputFile + "_Copy", "flight_id")  
    print("Copy of input file created and identical Flight ID's removed.")
    arcpy.AddMessage("Copy of input file created and identical Flight ID's removed.")    
    
    # Convert local DateTime field to text, then parse into HOUR and MONTH fields for later summarization
    print("Converting recorded DateTime to local time and creating new hour and month fields...")
    arcpy.AddMessage("Converting recorded DateTime to local time and creating new hour and month fields...")    
    arcpy.management.ConvertTimeField(inputFile + "_Copy", 'TIME', "", "TIME_TEXT", 'TEXT', "yyyy/MM/dd HH:mm:ss")
    arcpy.management.CalculateField(inputFile + "_Copy", "HOUR", "!TIME_TEXT![-8:-6]", 'PYTHON3')
    arcpy.management.CalculateField(inputFile + "_Copy", "MONTH", "!TIME_TEXT![-14:-12]", 'PYTHON3')
    print("Local time, hour, and month fields calculated.")
    arcpy.AddMessage("Local time, hour, and month fields calculated.") 
    
    print("Calculating flight summaries by hour and month (frequencies and percentages)...") 
    arcpy.AddMessage("Calculating flight summaries by hour and month (frequencies and percentages)...")       
    arcpy.analysis.Frequency(inputFile + "_Copy", outputTableNameHour, "HOUR")
    arcpy.analysis.Frequency(inputFile + "_Copy", outputTableNameMonth, "MONTH")      
    with arcpy.da.SearchCursor(outputTableNameHour, "FREQUENCY") as cursor:
        for row in cursor:
            totalFlights += row[0]
    arcpy.management.AddField(outputTableNameHour, "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField(outputTableNameMonth, "PERCENTAGE", "DOUBLE")    
    with arcpy.da.UpdateCursor(outputTableNameHour, ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalFlights * 100, 1)])            
    with arcpy.da.UpdateCursor(outputTableNameMonth, ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalFlights * 100, 1)])            
    print("Hourly and monthly flight summaries calculated.") 
    arcpy.AddMessage("Hourly and monthly flight summaries calculated.")
    
    # Delete copy of temporary merged waypoint file
    print("Deleting copy of merged waypoint input file...") 
    arcpy.AddMessage("Deleting copy of merged waypoint input file...")
    arcpy.management.Delete(inputFile + "_Copy")
    print("File successfully deleted.") 
    arcpy.AddMessage("File successfully deleted.")
  
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
    print("There are a total of {0} flights included in the summary.".format(str(totalFlights)))
    arcpy.AddMessage("There are a total of {0} unique flights included in the summary.".format(str(totalFlights)))
