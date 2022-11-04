# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_4.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Create waypoint and flightline files to further scrutinize suspected non-tourism flights.
    Status:  Development
    Date created: 2/22/2022
    Date last modified: 11/2/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
inputWaypoints = arcpy.GetParameterAsText(0)
inputFlightlines = arcpy.GetParameterAsText(1)
registrantValues = arcpy.GetParameterAsText(2)
sinuosityValues = arcpy.GetParameterAsText(3)
nameValues = arcpy.GetParameterAsText(4)
mileValue = arcpy.GetParameterAsText(5)
outputSuspectPoints = arcpy.GetParameterAsText(6)
outputSuspectLines = arcpy.GetParameterAsText(7)
outputScreenedMergedPoints = arcpy.GetParameterAsText(8)
outputScreenedMergedLines = arcpy.GetParameterAsText(9)

# Set local environments
arcpy.env.workspace = arcpy.Describe(inputWaypoints).path
arcpy.env.overwriteOutput = True

try:
    
    # Start timer and create progressor
    start = time.time()
    arcpy.SetProgressor("step", "Copying merged flightlines for screening...", 0, 10, 1)
       
    # Make a feature layer of the flightline file to be screened
    arcpy.management.CopyFeatures(inputFlightlines, outputScreenedMergedLines)
    tempFlightlines = arcpy.management.MakeFeatureLayer(outputScreenedMergedLines)
    
    # Select flightlines with TYPE_REGISTRANT equal to user-supplied list in registrantValues
    arcpy.SetProgressorLabel("Removing TYPE_REGISTRANT values from merged flightlines...")
    arcpy.SetProgressorPosition()
    newRegistrantValues = registrantValues.strip()
    splitRegistrantValues = newRegistrantValues.split(",")
    for value in splitRegistrantValues:
        whereClause = 'TYPE_REGISTRANT = {0}'.format(value)
        arcpy.management.SelectLayerByAttribute(tempFlightlines, 'ADD_TO_SELECTION', whereClause)
    arcpy.management.CopyFeatures(tempFlightlines, 'temp1')   
    count1 = arcpy.management.GetCount('temp1')
    print("Flights meeting TYPE_REGISTRANT criteria selected...")
    arcpy.AddMessage("Flights meeting TYPE_REGISTRANT criteria selected...")
    arcpy.management.DeleteFeatures(tempFlightlines)
        
    # Select flightlines with Sinuosity values between user-supplied minimum and maximum
    arcpy.SetProgressorLabel("Removing SINUOSITY values from merged flightlines...")
    arcpy.SetProgressorPosition()
    arcpy.management.SelectLayerByAttribute(tempFlightlines, "CLEAR_SELECTION")
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
    arcpy.management.DeleteFeatures(tempFlightlines)
    
    # Select commercial flightlines with NAME equal to user-supplied list in nameValues
    arcpy.SetProgressorLabel("Removing OPERATOR values from merged flightlines...")
    arcpy.SetProgressorPosition()
    arcpy.management.SelectLayerByAttribute(tempFlightlines, "CLEAR_SELECTION")
    newNameValues = nameValues.split(",")
    splitNameValues = [num.strip() for num in newNameValues]
    for name in splitNameValues:
        whereClause = "NAME = '{0}'".format(name)
        arcpy.management.SelectLayerByAttribute(tempFlightlines, 'ADD_TO_SELECTION', whereClause)
    arcpy.management.CopyFeatures(tempFlightlines, 'temp3')
    count3 = arcpy.management.GetCount('temp3')
    print("Flights meeting Operator Name criteria selected...")
    arcpy.AddMessage("Flights meeting Operator Name criteria selected...")           
    arcpy.management.DeleteFeatures(tempFlightlines)
    
    # Select flightlines with length in miles less than threshold in user-supplied mileValue
    arcpy.SetProgressorLabel("Removing flights less than MIN PATH LENGTH from merged flightlines...")
    arcpy.SetProgressorPosition()
    arcpy.management.SelectLayerByAttribute(tempFlightlines, "CLEAR_SELECTION")
    whereClause = "LengthMiles < {0}".format(mileValue)
    arcpy.management.SelectLayerByAttribute(tempFlightlines, 'NEW_SELECTION', whereClause)
    arcpy.management.CopyFeatures(tempFlightlines, 'temp4')
    count4 = arcpy.management.GetCount('temp4')
    arcpy.management.DeleteFeatures(tempFlightlines)
    print("Flights not meeting minimum path length selected...")
    arcpy.AddMessage("Flights not meeting minimum path length selected...")
    
    # Merge temporary files into single new screening flightline file and delete temp files
    arcpy.SetProgressorLabel("Merging suspect flightlines into output feature class.....")
    arcpy.SetProgressorPosition()
    arcpy.management.Merge(['temp1', 'temp2', 'temp3', 'temp4'], outputSuspectLines)
    arcpy.management.DeleteIdentical(outputSuspectLines, ['flight_id', 'LengthMiles', 'Sinuosity'])      
    count5 = arcpy.management.GetCount(outputSuspectLines)
    print("Suspect flightlines merged into screening featureclass...")
    arcpy.AddMessage("Suspect flightlines merged into screening featureclass...")            
    
    # Delete temporary files
    arcpy.SetProgressorLabel("Removing temporary files...")
    arcpy.SetProgressorPosition()
    delList = arcpy.ListFeatureClasses("temp*")
    for i in delList:
        arcpy.management.Delete(i)
    print("Temporary files removed from current workspace...")
    arcpy.AddMessage("Temporary files removed from current workspace...")
    
    # Create a list of flight_id's for screened flightlines to screen waypoints
    arcpy.SetProgressorLabel("Creating list of suspect FLIGHT ID's...")
    arcpy.SetProgressorPosition()      
    flightIdList = []
    with arcpy.da.SearchCursor(outputSuspectLines, 'flight_id') as cursor:
        for row in cursor:
            flightIdList.append(row[0])
    print("List of suspect Flight IDs created...")
    arcpy.AddMessage("List of suspect Flight IDs created...")             

    # Make a feature layer of the waypoints file to be cleaned
    arcpy.SetProgressorLabel("Creating feature class for suspect waypoints...")
    arcpy.SetProgressorPosition()    
    tempWaypoints = arcpy.management.MakeFeatureLayer(inputWaypoints)
    
    # Select flight_id's and save waypoints to new screening waypoint file
    flights = "', '".join(flightIdList)
    whereClause = "flight_id IN ('{}')".format(flights)
    arcpy.management.SelectLayerByAttribute(tempWaypoints, 'NEW_SELECTION', whereClause)
    arcpy.management.CopyFeatures(tempWaypoints, outputSuspectPoints)
    print("Feature class created for suspect waypoints...")
    arcpy.AddMessage("Feature class created for suspect waypoints...")
    
    # Switch selectioni and save waypoints to a new screened waypoint file
    arcpy.SetProgressorLabel("Removing suspect waypoints from new merged waypoint feature class...")
    arcpy.SetProgressorPosition()
    arcpy.management.SelectLayerByAttribute(tempWaypoints, 'SWITCH_SELECTION')
    arcpy.management.CopyFeatures(tempWaypoints, outputScreenedMergedPoints)
    print("Suspect waypoints removed from new merged waypoint feature class...")
    arcpy.AddMessage("Suspect waypoints removed from new merged waypoint feature class...")              

    # Reset the progressor
    arcpy.ResetProgressor()
    
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddError("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report aircraft and flight summaries and execution time
    end = time.time()
    print("There were {0} flights meeting the registrant type(s).".format(str(count1))) 
    arcpy.AddMessage("There were {0} flights meeting the registrant type(s).".format(str(count1)))
    print("There were {0} flights meeting sinuosity criteria.".format(str(count2))) 
    arcpy.AddMessage("There were {0} flights meeting sinuosity criteria.".format(str(count2)))
    print("There were {0} commercial flight identified.".format(str(count3))) 
    arcpy.AddMessage("There were {0} commercial flight providers identified.".format(str(count3)))
    print("There were {0} flights with flightpath lengths less than the minimum.".format(str(count4))) 
    arcpy.AddMessage("There were {0} flights with flightpath lengths less than the minimum.".format(str(count4)))
    print("There were a total of {0} suspect flights identified meeting screening criteria.".format(str(count5))) 
    arcpy.AddMessage("There were {0} suspect flights identified meeting screening criteria.".format(str(count5)))
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
