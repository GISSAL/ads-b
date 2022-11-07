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
inputFlightlines = arcpy.GetParameterAsText(1)
parkBoundaryFile = arcpy.GetParameterAsText(2)
bufferDistance = arcpy.GetParameterAsText(3)

# Set local environments
arcpy.env.workspace = arcpy.Describe(inputFlightlines).path
arcpy.env.overwriteOutput = True

# Fixed local variables
totalFlights = 0
operator_reclassTable = [[1, "Individual"], [2, "Partnership"], [3, "Corporation"], [4, "Co-Owned"], [5, "Government"], [7, "LLC"], [8, "Non-Citizen Corporation"], [9, "Non-Citizen Co-Owned"]]
type_reclassTable = [[1, "Glider"], [2, "Balloon"], [3, "Blimp/Dirigible"], [4, "Fixed Wing Single Engine"], [5, "Fixed Wing Multi Engine"], [6, "Rotorcraft"], [7, "Weight-Shift-Control"], [8, "Powered Parachute"], [9, "Gyroplane"]]

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Creating the buffer and clipping screened flightlines..", 0, 3, 1)
    
    # Create buffer polygon around park boundary based on user-defined distance, then clips the inputWaypoits
    arcpy.analysis.Buffer(parkBoundaryFile, "temp1", bufferDistance)
    arcpy.analysis.Clip(inputFlightlines,  "temp1", "temp2") 
    print("Buffer created and flightlines clipped.")    
    arcpy.AddMessage("Buffer created and flightlines clipped.")    
    
    # Calculate frequencies and percentages
    arcpy.SetProgressorLabel("Calculating flight operator and type frequencies and percentages...")
    arcpy.SetProgressorPosition()
    arcpy.analysis.Frequency("temp2", parkName + "_" + "FlightSummary_Operators", "TYPE_REGISTRANT")
    arcpy.analysis.Frequency("temp2", parkName + "_" + "FlightSummary_Type", "TYPE_AIRCRAFT")      
    with arcpy.da.SearchCursor(parkName + "_" + "FlightSummary_Operators", "FREQUENCY") as cursor:
        for row in cursor:
            totalFlights += row[0]
    arcpy.management.AddField(parkName + "_" + "FlightSummary_Operators", "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField(parkName + "_" + "FlightSummary_Type", "PERCENTAGE", "DOUBLE")    
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_Operators", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalFlights * 100, 1)])            
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_Type", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalFlights * 100, 1)])            
    print("Aircraft operator and type summaries calculated.") 
    arcpy.AddMessage("Aircraft operator and type summaries calculated.")
    
    # Reclassify operator and aircraft type numeric codes into descriptive text fields
    arcpy.SetProgressorLabel("Reclassifying aircraft operators and types...")
    arcpy.SetProgressorPosition()
    arcpy.management.ReclassifyField(parkName + "_" + "FlightSummary_Operators", "TYPE_REGISTRANT", "MANUAL", "", "", "", operator_reclassTable, "", "Aircraft_Operator")
    arcpy.management.ReclassifyField(parkName + "_" + "FlightSummary_Type", "TYPE_AIRCRAFT", "MANUAL", "", "", "", type_reclassTable, "", "Aircraft_Type")
    arcpy.management.DeleteField(parkName + "_" + "FlightSummary_Operators", "Aircraft_Operator_RANGE")
    arcpy.management.DeleteField(parkName + "_" + "FlightSummary_Type", "Aircraft_Type_RANGE")
    print("Reclassification complete.")
    arcpy.AddMessage("Reclassification complete.")

    # Reset the progressor
    arcpy.ResetProgressor()
     
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddError("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))
except:
    print("An unexpected error occurred processing the input file {0}".format(inputFlightlines))
    arcpy.AddWarning("An unexpected error occurred processing the input file {0}".format(inputFlightlines))
    
finally: 
    # Delete files no longer needed
    delList = arcpy.ListFeatureClasses("temp*")
    for i in delList:
        arcpy.management.Delete(i)
    
    # Report execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
    print("There are a total of {0} flights included in the summary.".format(str(totalFlights)))
    arcpy.AddMessage("There are a total of {0} unique flights included in the summary.".format(str(totalFlights)))
