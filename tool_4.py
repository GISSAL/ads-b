# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_4.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Create waypoint and flightline files for screening
    Status:  Development
    Date created: 2/22/2022
    Date last modified: 2/23/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
#inputWaypoints = arcpy.GetParameterAsText(0)
#inputFlightlines = arcpy.GetParameterAsText(1)
#registrantValue = arcpy.GetParameterAsText(2)
#sinuosityValue = arcpy.GetParameterAsText(3)
#nameValues = arcpy.GetParameterAsText(4)
#mileValue = arcpy.GetParameterAsText(5)
#outputWorkspace = arcpy.GetParameterAsText(6)
#outputCleanPoints = arcpy.GetParameterAsText(7)
#outputCleanLines = arcpy.GetParameterAsText(8)

# User-specified local variable(s) for stand-alone Python script
inputWaypoints = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/MergedWaypoints"
inputFlightlines = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/MergedFlightlines"
registrantValues = "5"  # Can enter a comma delimited list of values
sinuosityValues = "0.10, 0.99"  # Enter a minimum and maximum as comma separated values
nameValues = "'AMERICAN AIRLINES INC','DELTA AIR LINES INC'"
mileValue = 1 # Enter single minimum value for flightpath length in miles
outputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb"
outputScreenPoints = "ScreenMergedWaypoints"
outputScreenLines = "ScreenMergedFlightlines"

# Set local environments
arcpy.env.workspace = outputWorkspace
arcpy.env.overwriteOutput = True

try:
    
    # Start timer
    start = time.time()
        
    # Make a feature layer of the flightline file to be screened
    tempFlightlines = arcpy.management.MakeFeatureLayer(inputFlightlines)
    
    # Select flightlines with TYPE_REGISTRANT equal to user-supplied list in registrantValues
    newRegistrantValues = registrantValues.strip()
    splitRegistrantValues = newRegistrantValues.split(",")
    for value in splitRegistrantValues:
        whereClause = 'TYPE_REGISTRANT = {0}'.format(value)
        arcpy.management.SelectLayerByAttribute(tempFlightlines, 'ADD_TO_SELECTION', whereClause)
    arcpy.management.CopyFeatures(tempFlightlines, 'temp1')
    count1 = arcpy.management.GetCount('temp1')
    print("Flights meeting TYPE_REGISTRANT criteria selected...")
    arcpy.AddMessage("Flights meeting TYPE_REGISTRANT criteria selected...")
        
    # Select flightlines with Sinuosity values between user-supplied minimum and maximum
    splitSinuosityValues = sinuosityValues.split(",")
    newSinuosityValues = []
    for value in splitSinuosityValues:
        newS = value.replace(' ', '')
        newSinuosityValues.append(newS)
    whereClause = 'Sinuosity < {0} OR Sinuosity > {1}'.format(newSinuosityValues[0], newSinuosityValues[1])
    arcpy.management.SelectLayerByAttribute(tempFlightlines, 'NEW_SELECTION', whereClause)
    arcpy.management.CopyFeatures(tempFlightlines, 'temp2')
    count2 = arcpy.management.GetCount('temp2')
    print("Flights meeting Sinuosity criteria selected...")
    arcpy.AddMessage("Flights meeting Sinuosity criteria selected...")    
    
    # Select commercial flightlines with NAME equal to user-supplied list in nameValues
    arcpy.management.SelectLayerByAttribute(tempFlightlines, "CLEAR_SELECTION")
    newNameValues = nameValues.strip()
    splitNameValues = newNameValues.split(",")
    for name in splitNameValues:
        whereClause = "NAME = {0}".format(name)
        arcpy.management.SelectLayerByAttribute(tempFlightlines, 'ADD_TO_SELECTION', whereClause)
    arcpy.management.CopyFeatures(tempFlightlines, 'temp3')
    count3 = arcpy.management.GetCount('temp3')
    print("Flights meeting Operator Name criteria selected...")
    arcpy.AddMessage("Flights meeting Operator Name criteria selected...")        
   
    
    # Select flightlines with length in miles less than threshold in user-supplied mileValue
    arcpy.management.SelectLayerByAttribute(tempFlightlines, "CLEAR_SELECTION")
    whereClause = "LengthMiles < {0}".format(mileValue)
    arcpy.management.SelectLayerByAttribute(tempFlightlines, 'NEW_SELECTION', whereClause)
    arcpy.management.CopyFeatures(tempFlightlines, 'temp4')
    count4 = arcpy.management.GetCount('temp4')
    print("Flights meeting minimum path length criteria selected...")
    arcpy.AddMessage("Flights meeting minimum path length criteria selected...")        
    
    # Merge temporary files into single new screening flightline file and delete temp files
    arcpy.management.Merge(['temp1', 'temp2', 'temp3', 'temp4'], outputScreenLines)
    arcpy.management.DeleteIdentical(outputScreenLines, 'flight_id')
    print("Flightline feature class created for screening...")
    arcpy.AddMessage("Flightline feature class created for screening...")            
    delList = arcpy.ListFeatureClasses("temp*")
    for i in delList:
        arcpy.management.Delete(i)
    print("Intermediate data removed from current workspace...")
    arcpy.AddMessage("Intermediate data removed from current workspace...")
    
    # Create a list of flight_id's for screened flightlines to screen waypoints
    flightIdList = []
    with arcpy.da.SearchCursor(outputScreenLines, 'flight_id') as cursor:
        for row in cursor:
            flightIdList.append(row[0])
        
    # Make a feature layer of the waypoints file to be cleaned
    tempWaypoints = arcpy.management.MakeFeatureLayer(inputWaypoints)
        
    # Create a list from undesired flightline flight_id's 
    for flight in flightIdList:
        whereClause = "flight_id = '{0}'".format(flight)
        arcpy.management.SelectLayerByAttribute(tempWaypoints, 'ADD_TO_SELECTION', whereClause)
        
    # Save selected flight_id waypoints to new screening waypoint file
    arcpy.management.CopyFeatures(tempWaypoints, outputScreenPoints)
    print("Waypoint feature class created for screening...")
    arcpy.AddMessage("Waypoint feature class created for screening...")         
    
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report aircraft and flight summaries and execution time
    end = time.time()
    print("There were {0} total registrant flights removed.".format(str(count1))) 
    arcpy.AddMessage("There were {0} total registrant flights removed.".format(str(count1)))
    print("There were {0} total flights removed due to sinuosity.".format(str(count2))) 
    arcpy.AddMessage("There were {0} total flights removed due to sinuosity.".format(str(count2)))
    print("There were {0} total commerical flights removed.".format(str(count3))) 
    arcpy.AddMessage("There were {0} total commerical flights removed.".format(str(count3)))
    print("There were {0} total flights removed due to short flightpath lengths.".format(str(count4))) 
    arcpy.AddMessage("There were {0} total flights removed due to short flightpath lengths.".format(str(count4)))
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))