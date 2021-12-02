# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: grsm_script_3.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Calculates sinuosity and fractal dimension for flight lines and joins select fields from the FAA releasable database
    Status:  Development
    Date created: 10/8/2021
    Date last modified: 12/02/2021
    Python Version: 3.72
"""

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

# Import libraries
import arcpy, time

# User-specified local variable(s) for ArcGIS script tool
inputFile = arcpy.GetParameterAsText(0)
sinValue = arcpy.GetParameterAsText(1)
faaTable = arcpy.GetParameterAsText(2)

# User-specified local variable(s) for stand-alone Python script
#inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/ADSB_GRSM_20190925_Lines_25Miles"
#sinValue = 0.19
#faaTable = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/FAA_Releasable_Database.gdb"

#Fixed local variable(s)
inField1 = "ICAO_address"
joinTable1 = faaTable + "/MASTER"
joinField1 = "MODE_S_CODE_HEX"
fieldList1 = ["N_NUMBER", "TYPE_AIRCRAFT", "TYPE_ENGINE", "TYPE_REGISTRANT", "NAME", "MFR_MDL_CODE"]
inField2 = "MFR_MDL_CODE"
joinTable2 = faaTable + "/ACFTREF"
joinField2 = "CODE"
fieldList2 = "MODEL"

# Set local environments
arcpy.env.overwriteOutput = True
arcpy.env.workspace = arcpy.Describe(inputFile).path

# Define new functions for sinuosity and fractal dimension
codeblock1 = """
def getSinuosity(shape):
    length = shape.length
    d = math.sqrt((shape.firstPoint.X - shape.lastPoint.X) ** 2 + (shape.firstPoint.Y - shape.lastPoint.Y) ** 2)
    return d/length"""
codeblock2 = """
def getFractal(shape):
    length = shape.length
    d = math.sqrt((shape.firstPoint.X - shape.lastPoint.X) ** 2 + (shape.firstPoint.Y - shape.lastPoint.Y) ** 2)
    n = length / 100
    return math.log(n) / (math.log(n) + math.log(d/length))"""

try:
    
    # Start timer
    start = time.time()
    
    # Add new fields to store sinuosity and fractal dimension values
    arcpy.management.AddField(inputFile, "Sinuosity", "DOUBLE")
    arcpy.management.AddField(inputFile, "Fractal", "DOUBLE")
    print("New fields for sinuosity and fractical dimension created...")
    arcpy.AddMessage("New fields for sinuosity and fractical dimension created...")
    
    # Apply sinuosity and fractal dimension calculations
    arcpy.CalculateField_management(inputFile, "Sinuosity", "getSinuosity(!shape!)", "PYTHON3", codeblock1)
    arcpy.CalculateField_management(inputFile, "Fractal", "getFractal(!shape!)", "PYTHON3", codeblock2)
    print("Sinuosity and fractical dimension calculated for flight lines...")
    arcpy.AddMessage("Sinuosity and fractical dimension calculated for flight lines...")
    
    # Find flights with sinuosity less than the threshold value (e.g., 0.19) that is indicative of survey flights
    selFlight = arcpy.management.SelectLayerByAttribute(inputFile, "NEW_SELECTION", """%s = 0.19""" % arcpy.AddFieldDelimiters(inputFile, "Sinuosity"))    
    print("There are {0} flights with a sinuosity less than the threshold value of {1}.".format(len(selFlight), str(sinValue)))
    arcpy.AddMessage("There are {0} flights with a sinuosity less than the threshold value of {1}.".format(len(selFlight), str(sinValue)))
    
    ## Remove line feature classes with sinuosity less than the threshold value
    #if len(selFlight) > 0:
    #    arcpy.DeleteFeatures_management(selFlight)
    #else:
    #    pass
    
    # Strip whitespace from the MODE_S_CODE_HEX field in the FAA MASTER file
    arcpy.CalculateField_management(joinTable1, joinField1, "!MODE_S_CODE_HEX!.strip()", "PYTHON3")

    # Perform a table join to add FAA database variables from MASTER file
    arcpy.management.JoinField(inputFile, inField1, joinTable1, joinField1, fieldList1)
    print("FAA fields N_Number, Type_Aircraft, Type_Engine, Name, and MFR_MDL_Code joined from MASTER table...")
    arcpy.AddMessage("FAA fields N_Number, Type_Aircraft, Type_Engine, Name, and MFR_MDL_Code joined from MASTER table...")

    # Perform a table join to add FAA database variables from ACFTREF file
    arcpy.management.JoinField(inputFile, inField2, joinTable2, joinField2, fieldList2)   
    print("FAA field MODEL joined from ACFTREF table...")
    arcpy.AddMessage("FAA field MODEL joined from ACFTREF table...")
    
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report aircraft and flight summaries and execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))
