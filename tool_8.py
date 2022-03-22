# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: tool_8.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Density analysis of waypoints
    Status:  Development
    Date created: 12/15/2021
    Date last modified: 1/24/2022
    Python Version: 3.72
"""

# Import libraries
import arcpy, os, time

# User-specified local variable(s) for ArcGIS script tool
inputFile = arcpy.GetParameterAsText(0)
bufferFile = arcpy.GetParameterAsText(1)
outputWorkspace = arcpy.GetParameterAsText(2)
outputRaster = arcpy.GetParameterAsText(3)

# User-specified local variable(s) for stand-alone Python script
#inputFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/MergedWaypoints"
#bufferFile = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb/Buffer_GRSM_10Miles"
#outputWorkspace = "D:/GIS_Research/ResearchProjects/NPS_ADS_B/NPS_ADS_B_GRSM.gdb"
#outputRaster = "KernelDensity"

# Set local environments
arcpy.env.overwriteOutput = True
arcpy.env.mask = bufferFile
arcpy.env.extent = bufferFile

# Fixed local variables
altitude1 = 500
altitude2 = 1000
altitude3 = 1500
altitude4 = 2000
altitude5 = 2500

try:
    
    # Start timer
    start = time.time()
       
    # Calculate overall kernel density (points per square meter)
    print("Calculating overall kernel density...")
    arcpy.AddMessage("Calculating overall kernel density...")
    outKernel = arcpy.sa.KernelDensity(inputFile, "")
    outKernel.save(os.path.join(outputWorkspace, outputRaster))
    
    # Create altitude slices and compute kernel density for each slice
    print("Calculating kernel density from 0 to {0} MSL...".format(str(altitude1)))
    arcpy.AddMessage("Calculating kernel density from 0 to {0} MSL...".format(str(altitude1)))
    selRecs1 = arcpy.management.SelectLayerByAttribute(inputFile, "NEW_SELECTION", """ "altitude" <= %s """ %altitude1)
    outKernel1 = arcpy.sa.KernelDensity(selRecs1, "")
    outKernel1.save(os.path.join(outputWorkspace, outputRaster + "_" + str(altitude1)))
    
    print("Calculating kernel density from {0} to {1} MSL...".format(str(altitude1), str(altitude2)))
    arcpy.AddMessage("Calculating kernel density from {0} to {1} MSL...".format(str(altitude1), str(altitude2)))
    selRecs2 = arcpy.management.SelectLayerByAttribute(inputFile, "NEW_SELECTION", """ "altitude" > %s  and "altitude" <= %s """ % (altitude1, altitude2))
    outKernel2 = arcpy.sa.KernelDensity(selRecs2, "")
    outKernel2.save(os.path.join(outputWorkspace, outputRaster + "_" + str(altitude2)))
    
    print("Calculating kernel density from {0} to {1} MSL...".format(str(altitude2), str(altitude3)))
    arcpy.AddMessage("Calculating kernel density from {0} to {1} MSL...".format(str(altitude2), str(altitude3)))
    selRecs3 = arcpy.management.SelectLayerByAttribute(inputFile, "NEW_SELECTION", """ "altitude" > %s  and "altitude" <= %s """ % (altitude2, altitude3))
    outKernel3 = arcpy.sa.KernelDensity(selRecs3, "")
    outKernel3.save(os.path.join(outputWorkspace, outputRaster + "_" + str(altitude3)))

    print("Calculating kernel density from {0} to {1} MSL...".format(str(altitude3), str(altitude4)))
    arcpy.AddMessage("Calculating kernel density from {0} to {1} MSL...".format(str(altitude3), str(altitude4)))
    selRecs4 = arcpy.management.SelectLayerByAttribute(inputFile, "NEW_SELECTION", """ "altitude" > %s  and "altitude" <= %s """ % (altitude3, altitude4))
    outKernel4 = arcpy.sa.KernelDensity(selRecs4, "")
    outKernel4.save(os.path.join(outputWorkspace, outputRaster + "_" + str(altitude4)))

    print("Calculating kernel density from {0} to {1} MSL...".format(str(altitude4), str(altitude5)))
    arcpy.AddMessage("Calculating kernel density from {0} to {1} MSL...".format(str(altitude4), str(altitude5)))
    selRecs5 = arcpy.management.SelectLayerByAttribute(inputFile, "NEW_SELECTION", """ "altitude" > %s  and "altitude" <= %s """ % (altitude4, altitude5))
    outKernel5 = arcpy.sa.KernelDensity(selRecs5, "")
    outKernel5.save(os.path.join(outputWorkspace, outputRaster + "_" + str(altitude5)))

    print("Calculating kernel density above {0} MSL...".format(str(altitude5)))
    arcpy.AddMessage("Calculating kernel density above {0} MSL...".format(str(altitude5)))
    selRecs6 = arcpy.management.SelectLayerByAttribute(inputFile, "NEW_SELECTION", """ "altitude" > %s """ %altitude5)
    outKernel6 = arcpy.sa.KernelDensity(selRecs6, "")
    outKernel6.save(os.path.join(outputWorkspace, outputRaster + "_Above_" + str(altitude5)))
    
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

finally:    
    # Report execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))    
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(str(round(end - start, 3))))