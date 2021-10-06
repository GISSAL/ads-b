# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: script4.py
    Author: Shawn Hutchinson
    Description:  Join flight lines with select fields in FAA releasable database
    Date created: 10/1/2021
    Date last modified: 10/1/2021
    Python Version: 3.7
"""

# Import libraries
import arcpy

# Local variable(s)
inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B.gdb/ADSB_HAVO_20190713_Lines_25Miles_AGL"
inField1 = "HexID"
joinTable1 = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/FAA_Releasable_Database/FAA_Releasable_Database.gdb/MASTER"
joinField1 = "MODE_S_CODE_HEX"
fieldList1 = ["N_NUMBER", "TYPE_AIRCRAFT", "TYPE_ENGINE", "TYPE_REGISTRANT", "NAME", "MFR_MDL_CODE"]
inField2 = "MFR_MDL_CODE"
joinTable2 = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/FAA_Releasable_Database/FAA_Releasable_Database.gdb/ACFTREF"
joinField2 = "CODE"
fieldList2 = "MODEL"

# Set local environments
arcpy.env.overwriteOutput = True

# Strip whitespace from the MODE_S_CODE_HEX field in the FAA MASTER file
arcpy.CalculateField_management(joinTable1, "joinField1", "!MODE_S_CODE_HEX!.strip()", "PYTHON3")

# Perform a table join to add FAA database variables from MASTER file
arcpy.management.JoinField(inputFile, inField1, joinTable1, joinField1, fieldList1)

# Perform a table join to add FAA database variables from ACFTREF file
arcpy.management.JoinField(inputFile, inField2, joinTable2, joinField2, fieldList2)


#Type Aircraft
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
#
#Type Engine
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
#
#Type Registrant
#1 - Individual
#2 - Partnership
#3 - Corporation
#4 - Co-Owned
#5 - Government
#7 - LLC
#8 - Non-Citizen Corporation
#9 - Non-Citizen Co-Owned
