# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_2.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Ingests processed ADS-B data and produces point and line feature classes with sinuosity values and joined FAA database fields
    Status:  Development
    Date created: 10/7/2021
    Date last modified: 2/23/2022
    Python Version: 3.7
"""
# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
inputFile = arcpy.GetParameterAsText(0)
parkBoundaryFile = arcpy.GetParameterAsText(1)
bufferDistance = arcpy.GetParameterAsText(2)
mslFilter = arcpy.GetParameterAsText(3)
inputDEM = arcpy.GetParameterAsText(4)
faaTable = arcpy.GetParameterAsText(5)
outputWorkspace = arcpy.GetParameterAsText(6)

# User-specified local variable(s) for stand-alone Python script
#inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/Outputs/ADSB_GRSM_20190926.csv"
#parkBoundaryFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/Boundary_GRSM"
#bufferDistance = "10 Miles"
#mslFilter = 9000
#inputDEM = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/DEM_10_GRSM"
#faaTable = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/FAA_Releasable_Database.gdb"
#outputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb"

# FAA Releasable Database MASTER Fields Key
# Type Aircraft
#1 - Glider
#2 - Balloon
#3 - Blimp/Dirigible
#4 - Fixed wing single engine
#5 - Fixed wing multi engine
#6 - Rotorcraft
#7 - Weight-shift-control
#8 - Powered Parachute
#9 - Gyroplane
#H - Hybrid Lift
#O - Other

# Type Engine
#0 - None
#1 - Reciprocating
#2 - Turbo-prop
#3 - Turbo-shaft
#4 - Turbo-jet
#5 - Turbo-fan
#6 - Ramjet
#7 - 2 Cycle
#8 - 4 Cycle
#9 – Unknown
#10 – Electric
#11 - Rotary

# Type Registrant
#1 - Individual
#2 - Partnership
#3 - Corporation
#4 - Co-Owned
#5 - Government
#7 - LLC
#8 - Non-Citizen Corporation
#9 - Non-Citizen Co-Owned

# Fixed local variable(s)
spatialRef = arcpy.SpatialReference(4269)
inField1 = "ICAO_address"
joinTable1 = faaTable + "/MASTER"
joinField1 = "MODE_S_CODE_HEX"
fieldList1 = ["N_NUMBER", "TYPE_AIRCRAFT", "TYPE_ENGINE", "TYPE_REGISTRANT", "NAME", "MFR_MDL_CODE"]
inField2 = "MFR_MDL_CODE"
joinTable2 = faaTable + "/ACFTREF"
joinField2 = "CODE"
fieldList2 = "MODEL"

# Define new functions for sinuosity calculation
codeblock1 = """
def getSinuosity(shape):
    length = shape.length
    d = math.sqrt((shape.firstPoint.X - shape.lastPoint.X) ** 2 + (shape.firstPoint.Y - shape.lastPoint.Y) ** 2)
    return d/length"""

# Set local environments
arcpy.env.workspace = outputWorkspace
arcpy.env.overwriteOutput = True

try:
    
    # Start timer
    start = time.time()
    
    if arcpy.CheckExtension("Spatial") == "Available":
        
        # Parse park name and output filename from local input variables
        outputFile = arcpy.Describe(inputFile).baseName
        parkName = outputFile[5:9]
        print("Reading in ADS-B waypoint data from {0}...".format(outputFile))
        arcpy.AddMessage("Reading in waypoint data from {0}...".format(outputFile))
        
        # Create point features
        arcpy.management.XYTableToPoint(inputFile, "temp1", "lon", "lat", "altitude", spatialRef)
        print("Point feature class created from ADS-B input file...")
        arcpy.AddMessage("Point feature class created from ADS-B input file...")
        
        # Check for an existing park buffer file and use it, or create a new buffer file to screen waypoints
        if arcpy.Exists("Buffer_" + parkName + "_" + bufferDistance.replace(" ", "")):
            print("Park buffer file already exists.  Moving to next process...")
            arcpy.AddMessage("Park buffer file already exists.  Moving to next process...")
            arcpy.analysis.Clip("temp1", "Buffer_" + parkName + "_" + bufferDistance.replace(" ", ""), "temp2")
            print("Waypoints outside buffer removed...")
            arcpy.AddMessage("Waypoints outside buffer removed...")
        else:
            arcpy.analysis.Buffer(parkBoundaryFile, "Buffer_" + parkName + "_" + bufferDistance.replace(" ", ""), bufferDistance)
            arcpy.analysis.Clip("temp1", "Buffer_" + parkName + "_" + bufferDistance.replace(" ", ""), "temp2")
            print("Park buffer generated and waypoints outside buffer removed...")
            arcpy.AddMessage("Park buffer generated and waypoints outside buffer removed...")      
        
        # Convert altitude (MSL) units converted from meters to feet and screen waypoints above threshold
        arcpy.management.CalculateField("temp2", "alt_msl", "int(!altitude! * 3.28084)", "PYTHON3", "", "LONG")
        arcpy.analysis.Select("temp2", "temp3", """"alt_msl" <= %s""" %mslFilter)
        print("Waypoints with altitudes above user-defined threshold removed...")
        arcpy.AddMessage("Waypoints with altitudes above user-defined threshold removed...")        

        # Perform AGL calculations and add new attribute field to waypoints
        arcpy.sa.ExtractValuesToPoints("temp3", inputDEM,  outputFile + "_Points_" + bufferDistance.replace(" ", ""))
        arcpy.management.CalculateField(outputFile + "_Points_" + bufferDistance.replace(" ", ""), "alt_agl", "int(!altitude! - !RASTERVALU! * 3.28084)", "PYTHON3", "", "LONG")
        arcpy.management.DeleteField(outputFile + "_Points_" + bufferDistance.replace(" ", ""), ["RASTERVALU"])
        print("Aircraft altitude above ground level (AGL in feet) calculated...")
        arcpy.AddMessage("Aircraft altitude above ground level (AGL in feet) calculated...")
        
        # Create line feature class from screened waypoints
        arcpy.management.PointsToLine(outputFile + "_Points_" + bufferDistance.replace(" ", ""), "temp4", "flight_id", "TIME")
        
        # Retain only line features with > 0 length (0 length indicates 2 input waypoints with same x- and y-coordinate values)
        selRecs = arcpy.management.SelectLayerByAttribute("temp4", "NEW_SELECTION", "Shape_Length > 0")
        arcpy.management.CopyFeatures(selRecs, outputFile + "_Lines_" + bufferDistance.replace(" ", ""))
        
        # Add a new field to store ICAO address, retrieve values from FlightID, and flightline length (miles)
        arcpy.management.AddField(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), "ICAO_address", "TEXT")
        arcpy.CalculateField_management(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), "ICAO_address", "!flight_id![:6]", "PYTHON3")
        arcpy.management.CalculateGeometryAttributes(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), [["LengthMiles", "LENGTH_GEODESIC"]], "MILES_US")
        print("Line feature class created from ADS-B waypoint data...")
        arcpy.AddMessage("Line feature class created from ADS-B waypoint data...")


        # Add new field to store sinuosity values
        arcpy.management.AddField(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), "Sinuosity", "FLOAT")    
        print("New field for sinuosity created...")
        arcpy.AddMessage("New field for sinuosity created...")
        
        # Apply sinuosity calculation
        arcpy.CalculateField_management(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), "Sinuosity", "getSinuosity(!Shape!)", "PYTHON3", codeblock1)
        print("Sinuosity calculated for flight lines...")
        arcpy.AddMessage("Sinuosity metric calculated for flight lines...")
              
        # Strip whitespace from the MODE_S_CODE_HEX field in the FAA MASTER file
        arcpy.CalculateField_management(joinTable1, joinField1, "!MODE_S_CODE_HEX!.strip()", "PYTHON3")
    
        # Perform a table join to add FAA database variables from MASTER file
        arcpy.management.JoinField(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), inField1, joinTable1, joinField1, fieldList1)
        print("FAA fields N_Number, Type_Aircraft, Type_Engine, Name, and MFR_MDL_Code joined from MASTER table...")
        arcpy.AddMessage("FAA fields N_Number, Type_Aircraft, Type_Engine, Name, and MFR_MDL_Code joined from MASTER table...")
    
        # Perform a table join to add FAA database variables from ACFTREF file
        arcpy.management.JoinField(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), inField2, joinTable2, joinField2, fieldList2)   
        print("FAA field MODEL joined from ACFTREF table...")
        arcpy.AddMessage("FAA field MODEL joined from ACFTREF table...")
        
        # Count number of aircraft with "null" N-Numbers (i.e., aircraft not in FAA database)
        selFlight1 = arcpy.management.SelectLayerByAttribute(outputFile + "_Lines_" + bufferDistance.replace(" ", ""), "NEW_SELECTION", "N_NUMBER IS NULL")
        count1 = arcpy.management.GetCount(selFlight1)
              
        # Delete files no longer needed
        delList = arcpy.ListFeatureClasses("temp*")
        for i in delList:
            arcpy.management.Delete(i)
        print("Intermediate data removed from current workspace...")
        arcpy.AddMessage("Intermediate data removed from current workspace...")

    else:
        arcpy.AddMessage("An ArcGIS Spatial Analyst extension is required!  The current status of this extension is {0}.".format(arcpy.CheckExtension("Spatial")))
        
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report aircraft and flight summaries and execution time
    end = time.time()
    print("There are {0} total aircraft with null values for N-Number.".format(str(count1))) 
    arcpy.AddMessage("There are {0} total aircraft with null values for N-Number.".format(str(count1)))
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
