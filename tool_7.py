# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_7.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Calculate flight summaries by operator using waypoints.
    Status:  Development
    Date created: 2/8/2022
    Date last modified: 2/8/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
inputFile = arcpy.GetParameterAsText(0)
outputWorkspace = arcpy.GetParameterAsText(1)
outputTableNameOperator = arcpy.GetParameterAsText(2)
outputTableNameType = arcpy.GetParameterAsText(3)

# User-specified local variable(s) for stand-alone Python script
#inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/MergedFlightlines"
#outputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb"
#outputTableNameOperator = "FlightSummary_Operators"
#outputTableNameType = "FlightSummary_AircraftType"

# Set local environments
arcpy.env.workspace = outputWorkspace
arcpy.env.overwriteOutput = True

# Fixed local variables
totalFlights = 0
operator_reclassTable = [[1, "Individual"], [2, "Partnership"], [3, "Corporation"], [4, "Co-Owned"], [5, "Government"], [7, "LLC"], [8, "Non-Citizen Corporation"], [9, "Non-Citizen Co-Owned"]]
type_reclassTable = [[1, "Glider"], [2, "Balloon"], [3, "Blimp/Dirigible"], [4, "Fixed Wing Single Engine"], [5, "Fixed Wing Multi Engine"], [6, "Rotorcraft"], [7, "Weight-Shift-Control"], [8, "Powered Parachute"], [9, "Gyroplane"]]

try:
    
    # Start timer
    start = time.time()
    
    # Create a temporary copy of the merged flightline file (all flightlines have unique ICAO addresses and flight id's
    print("Creating a temporary copy of the merged flightline input file...")
    arcpy.AddMessage("Creating a temporary copy of the merged flightline input file...")    
    arcpy.management.Copy(inputFile, inputFile + "_Copy")
    print("Copy of input file created.")
    arcpy.AddMessage("Copy of input file created.")    
      
    print("Calculating flight operator and aircraft type summaries(frequencies and percentages)...") 
    arcpy.AddMessage("Calculating flight operator and aircraft type summaries(frequencies and percentages)...") 
    arcpy.analysis.Frequency(inputFile + "_Copy", outputTableNameOperator, "TYPE_REGISTRANT")
    arcpy.analysis.Frequency(inputFile + "_Copy", outputTableNameType, "TYPE_AIRCRAFT")      
    with arcpy.da.SearchCursor(outputTableNameOperator, "FREQUENCY") as cursor:
        for row in cursor:
            totalFlights += row[0]
    arcpy.management.AddField(outputTableNameOperator, "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField(outputTableNameType, "PERCENTAGE", "DOUBLE")    
    with arcpy.da.UpdateCursor(outputTableNameOperator, ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalFlights * 100, 1)])            
    with arcpy.da.UpdateCursor(outputTableNameType, ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalFlights * 100, 1)])            
    print("Flight summaries by operator and aircraft type.") 
    arcpy.AddMessage("Flight summaries by operator and aircraft type.")
    
    
    # Reclassify operator and aircraft type numeric codes into descriptive text fields
    print("Reclassifying operator and aircraft type codes...")
    arcpy.AddMessage("Reclassifying operator and aircraft type codes...")
    arcpy.management.ReclassifyField(outputTableNameOperator, "TYPE_REGISTRANT", "MANUAL", "", "", "", operator_reclassTable, "", "Aircraft_Operator")
    arcpy.management.ReclassifyField(outputTableNameType, "TYPE_AIRCRAFT", "MANUAL", "", "", "", type_reclassTable, "", "Aircraft_Type")
    arcpy.management.DeleteField(outputTableNameOperator, "Aircraft_Operator_RANGE")
    #arcpy.management.AlterField(outputTableNameOperator, "Aircraft_Operator_CLASS", "Aircraft_Operator", "Aircraft Operator", "TEXT", 30)
    arcpy.management.DeleteField(outputTableNameType, "Aircraft_Type_RANGE")
    #arcpy.management.AlterField(outputTableNameType, "Aircraft_Type_CLASS", "Aircraft_Type", "Aircraft Type", "TEXT", 30)
    print("Reclassification complete.")
    arcpy.AddMessage("Reclassification complete.")
    
    # Delete copy of temporary merged flightline file
    print("Deleting copy of merged flightline input file...") 
    arcpy.AddMessage("Deleting copy of merged flightline input file...")
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
