# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: ads_b_tool_6.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Generates output tables summarizing waypoint frequencies by day, hour, month/year, aircraft operator, and aircraft type.
    Status:  Development
    Date created: 1/24/2022
    Date last modified: 12/16/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
parkName = arcpy.GetParameterAsText(0)
inputWaypoints = arcpy.GetParameterAsText(1)
faaTable = arcpy.GetParameterAsText(2)

# Set local environments
arcpy.env.workspace = arcpy.Describe(inputWaypoints).path
arcpy.env.overwriteOutput = True

# Fixed local variables
inField1 = "ICAO_address"
joinTable1 = faaTable + "/MASTER"
joinField1 = "MODE_S_CODE_HEX"
fieldList1 = ["TYPE_AIRCRAFT", "TYPE_REGISTRANT"]
operator_reclassTable = [[1, "Individual"], [2, "Partnership"], [3, "Corporation"], [4, "Co-Owned"], [5, "Government"], [7, "LLC"], [8, "Non-Citizen Corporation"], [9, "Non-Citizen Co-Owned"]]
type_reclassTable = [[1, "Glider"], [2, "Balloon"], [3, "Blimp/Dirigible"], [4, "Fixed Wing Single Engine"], [5, "Fixed Wing Multi Engine"], [6, "Rotorcraft"], [7, "Weight-Shift-Control"], [8, "Powered Parachute"], [9, "Gyroplane"]]

# Define function for determining the type of day - weekday or weekend
codeblock1 = """
def getDayType(labelday):
    daynum = labelday.weekday()
    if daynum < 5:
        return "Weekday"
    else:
        return "Weekend"
"""

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Creating the buffer and clipping screened waypoints..", 0, 6, 1)
    
    # Copy input waypoint file to a temp file and delete identical flight_id's to represent flights
    arcpy.SetProgressorLabel("Creating a temporary copy of the input waypoint file...")
    arcpy.SetProgressorPosition()   
    arcpy.management.CopyFeatures(inputWaypoints, "temp1")    
    arcpy.management.DeleteIdentical("temp1", "flight_id")  
    print("Input waypoint feature class copied.")    
    arcpy.AddMessage("Input waypoint feature class copied.")    

    # Convert local DateTime field to text, then parse into HOUR and MONTH fields for later summarization
    arcpy.SetProgressorLabel("Converting DateTime to local time and creating new hour and month fields...")
    arcpy.SetProgressorPosition()
    arcpy.management.ConvertTimeField("temp1", 'TIME', "", "TIME_TEXT", 'TEXT', "yyyy/MM/dd HH:mm:ss")
    arcpy.management.CalculateField("temp1", "DAY", "!TIME!.strftime('%A')", "PYTHON3")
    arcpy.management.CalculateField("temp1", "HOUR", "!TIME_TEXT![-8:-6]", 'PYTHON3')
    arcpy.management.CalculateField("temp1", "MONTH", "!TIME_TEXT![-14:-12]", 'PYTHON3')
    arcpy.management.CalculateField("temp1", "YEAR", "!TIME_TEXT![0:4]", 'PYTHON3')
    arcpy.management.CalculateField("temp1", "MOYEAR", "!MONTH! + '/' + !YEAR!", 'PYTHON3')
    print("Local time conversion complete; hour and month fields calculated.")    
    arcpy.AddMessage("Local time conversion complete; hour and month fields calculated.")    
    
    # Calculate frequencies and percentages for day, hour, and month/year tables
    arcpy.SetProgressorLabel("Calculating day, hour, and month frequencies and percentages...")
    arcpy.SetProgressorPosition()     
    arcpy.analysis.Frequency("temp1", parkName + "_" + "FlightSummary_HR", "HOUR")
    totalWaypoints = 0
    with arcpy.da.SearchCursor(parkName + "_" + "FlightSummary_HR", "FREQUENCY") as cursor:
        for row in cursor:
            totalWaypoints += row[0]
    arcpy.management.AddField(parkName + "_" + "FlightSummary_HR", "PERCENTAGE", "DOUBLE")
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_HR", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])         
    arcpy.analysis.Frequency("temp1", parkName + "_" + "FlightSummary_DAY", "DAY")
    arcpy.management.AddField(parkName + "_" + "FlightSummary_DAY", "PERCENTAGE", "DOUBLE")
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_DAY", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])              
    arcpy.analysis.Frequency("temp1", parkName + "_" + "FlightSummary_MOYR", "MOYEAR")              
    arcpy.management.AddField(parkName + "_" + "FlightSummary_MOYR", "PERCENTAGE", "DOUBLE")    
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_MOYR", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])            
    print("Day, hour, and month flight summaries calculated.") 
    arcpy.AddMessage("Day, hour, and month flight summaries calculated.")     
    
    # Calculate frequencies and percentages for flights by hour for weekdays and weekends
    arcpy.CalculateField_management("temp1", "DAYTYPE", "getDayType(!TIME!)", "PYTHON3", codeblock1)
    arcpy.analysis.Frequency("temp1", parkName + "_" + "FlightSummary_DAYTYPE2", ["HOUR", "DAYTYPE"])
    arcpy.management.Sort(parkName + "_" + "FlightSummary_DAYTYPE2", parkName + "_" + "FlightSummary_DAYTYPE", "DAYTYPE")
    arcpy.management.Delete(parkName + "_" + "FlightSummary_DAYTYPE2")
    arcpy.management.AddField(parkName + "_" + "FlightSummary_DAYTYPE", "PERCENTAGE", "DOUBLE")  
    totalWeekdays = 0
    with arcpy.da.SearchCursor(parkName + "_" + "FlightSummary_DAYTYPE", "FREQUENCY", "DAYTYPE = 'Weekday'") as cursor:
        for row in cursor:
            totalWeekdays += row[0]
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_DAYTYPE", ("FREQUENCY", "PERCENTAGE"), "DAYTYPE = 'Weekday'") as cursor:
        for frequency, percentage in cursor:
            cursor.updateRow([frequency, round(frequency / totalWeekdays * 100, 1)])       
    print("{0} weekday flights identified and hourly summaries calculated.".format(totalWeekdays)) 
    arcpy.AddMessage("{0} weekday flights identified and hourly summaries calculated.".format(totalWeekdays)) 
    totalWeekends = 0    
    with arcpy.da.SearchCursor(parkName + "_" + "FlightSummary_DAYTYPE", "FREQUENCY", "DAYTYPE = 'Weekend'") as cursor:
        for row in cursor:
            totalWeekends += row[0]
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_DAYTYPE", ("FREQUENCY", "PERCENTAGE"), "DAYTYPE = 'Weekend'") as cursor:
        for frequency, percentage in cursor:
            cursor.updateRow([frequency, round(frequency / totalWeekends * 100, 1)])       
    arcpy.management.DeleteField(parkName + "_" + "FlightSummary_DAYTYPE", "ORIG_FID")
    print("{0} weekend flights identified and hourly summaries calculated.".format(totalWeekends)) 
    arcpy.AddMessage("{0} weekend flights identified and hourly summaries calculated.".format(totalWeekends))    

    # Strip whitespace from the MODE_S_CODE_HEX field in the FAA MASTER file
    arcpy.SetProgressorLabel("Joining select fields from MASTER table of FAA Releaseable Database...")
    arcpy.SetProgressorPosition()
    arcpy.CalculateField_management(joinTable1, joinField1, "!MODE_S_CODE_HEX!.strip()", "PYTHON3")
    
    # Perform a table join to add FAA database variables from MASTER file
    arcpy.management.JoinField("temp1", inField1, joinTable1, joinField1, fieldList1)
    print("Type_Aircraft and Type_Registrant fields joined from FAA MASTER table.")    
    arcpy.AddMessage("Type_Aircraft and Type_Registrant fields joined from FAA MASTER table.") 
  
    # Need to make TYPE_REGISTRANT field in temp1 an INT to allow for later reclassification
    arcpy.management.AddField("temp1", "TYPE_OPERATOR", "SHORT")
    arcpy.management.CalculateField("temp1", "TYPE_OPERATOR", "!TYPE_REGISTRANT!", "PYTHON3")
    
    # Calculate frequencies and percentages for flight operators and aircraft types
    arcpy.SetProgressorLabel("Calculating flight operator and type frequencies and percentages...")
    arcpy.SetProgressorPosition()
    
    totalWaypoints = 0
    arcpy.analysis.Frequency("temp1", parkName + "_" + "FlightSummary_Operators", "TYPE_OPERATOR")
    arcpy.analysis.Frequency("temp1", parkName + "_" + "FlightSummary_Type", "TYPE_AIRCRAFT")      
    with arcpy.da.SearchCursor(parkName + "_" + "FlightSummary_Operators", "FREQUENCY") as cursor:
        for row in cursor:
            totalWaypoints += row[0]
    arcpy.management.AddField(parkName + "_" + "FlightSummary_Operators", "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField(parkName + "_" + "FlightSummary_Type", "PERCENTAGE", "DOUBLE")    
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_Operators", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])            
    with arcpy.da.UpdateCursor(parkName + "_" + "FlightSummary_Type", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints * 100, 1)])            
    print("Aircraft operator and type summaries calculated.") 
    arcpy.AddMessage("Aircraft operator and type summaries calculated.")
    
    # Reclassify operator and aircraft type numeric codes into descriptive text fields
    arcpy.SetProgressorLabel("Reclassifying aircraft operators and types...")
    arcpy.SetProgressorPosition()
    arcpy.management.ReclassifyField(parkName + "_" + "FlightSummary_Operators", "TYPE_OPERATOR", "MANUAL", "", "", "", operator_reclassTable, "", "Aircraft_Operator")
    arcpy.management.ReclassifyField(parkName + "_" + "FlightSummary_Type", "TYPE_AIRCRAFT", "MANUAL", "", "", "", type_reclassTable, "", "Aircraft_Type")
    arcpy.management.DeleteField(parkName + "_" + "FlightSummary_Operators", "Aircraft_Operator_RANGE")
    arcpy.management.DeleteField(parkName + "_" + "FlightSummary_Type", "Aircraft_Type_RANGE")
    print("Reclassification of aircraft operators and types complete.")
    arcpy.AddMessage("Reclassification of aircraft operators and types complete.")  

    # Report final aircraft summaries
    print("Success... Aircraft flights summarized!")
    arcpy.AddMessage("Success... Aircraft flight summarized!")
    print("A total of {0} flights were used to generate the summary data.".format(str(totalWaypoints)))
    arcpy.AddMessage("A total of {0} flights were used to generate the summary data.".format(str(totalWaypoints)))
           
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
    print("Temporary files deleted.")

    # Report execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 1))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 1))))
    
    # Reset the progressor
    arcpy.ResetProgressor()
