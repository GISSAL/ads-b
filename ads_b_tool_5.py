# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    File name: ads_b_tool_5.py
    Author: Shawn Hutchinson
    Credits: Shawn Hutchinson, Brian Peterson
    Description:  Generates output tables summarizing waypoint altitudes (both MSL and AGL) by user-defined classes, creates kernel density grids for each AGL class, and produces optional band collection statistics
    Status:  Development
    Date created: 1/24/2022
    Date last modified: 3/22/2023
    Python Version: 3.72
"""

# Create custom error class
class WhitespaceError(Exception):
    pass

# Import libraries
import arcpy, time, os

# User-specified local variable(s) for ArcGIS script tool
parkName = arcpy.GetParameterAsText(0)
inputWaypoints = arcpy.GetParameterAsText(1)
parkBoundaryFile = arcpy.GetParameterAsText(2)
bufferDistance = arcpy.GetParameterAsText(3)
aglMin = arcpy.GetParameterAsText(4)
aglMax = arcpy.GetParameterAsText(5)
aglInterval = arcpy.GetParameterAsText(6)
mslMin = arcpy.GetParameterAsText(7)
mslMax = arcpy.GetParameterAsText(8)
mslInterval = arcpy.GetParameterAsText(9)
outputWaypoints = arcpy.GetParameterAsText(10)
outputTable = arcpy.GetParameterAsText(11)  #Optional correlation matrix text file

# Set local environments
arcpy.env.workspace = arcpy.Describe(inputWaypoints).path
arcpy.env.overwriteOutput = True
arcpy.env.extent = inputWaypoints

# Parallel Processing Factor - applies only to Buffer. Clip, and Kernel Density functions
arcpy.env.parallelProcessingFactor = "50%"

# Fixed local variables
totalWaypoints_agl = 0
totalWaypoints_msl = 0
totalFlights_agl = 0
totalFlights_msl = 0
aglClasses = round(int(aglMax)/int(aglInterval))
mslClasses = round(int(mslMax)/int(mslInterval))

try:
    
    # Start timer and create progressor
    start = time.time()
  
    # Create buffer polygon around park boundary based on user-defined distance, then clip the inputFile
    arcpy.SetProgressor("step", "Creating the buffer and clipping screened waypoints...", 0, 8, 1)
    arcpy.analysis.Buffer(parkBoundaryFile, "temp1", bufferDistance)
    arcpy.analysis.Clip(inputWaypoints,  "temp1", "temp2")
    print("Buffer created and waypoints clipped.")    
    arcpy.AddMessage("Buffer created and waypoints clipped.")    
   
    # Delete waypoints with AGL/MSL greater than the maximum value that won't be included in the summary tables
    arcpy.SetProgressorLabel("Removing waypoints outside of desired altitude bands...")
    arcpy.SetProgressorPosition()    
    tempWaypoints = arcpy.management.MakeFeatureLayer("temp2")  
    arcpy.analysis.Select(tempWaypoints, "temp3", """{0} <= {1}""".format(arcpy.AddFieldDelimiters(tempWaypoints, "alt_agl"), aglMax))
    arcpy.analysis.Select(tempWaypoints, "temp4", """{0} <= {1}""".format(arcpy.AddFieldDelimiters(tempWaypoints, "alt_msl"), mslMax))
    print("Selected waypoints removed.")    
    arcpy.AddMessage("Selected waypoints removed.")

    # Save refined AGL waypoints file for use in later summaries
    arcpy.SetProgressorLabel("Creating new output AGL waypoints feature class...")
    arcpy.SetProgressorPosition()
    arcpy.management.CopyFeatures("temp3", outputWaypoints)
    print("New output AGL waypoints feature class created.")    
    arcpy.AddMessage("New output AGL waypoints feature class created.")       

    # Determine the number of unique flights within the AGL and MSL datasets
    arcpy.SetProgressorLabel("Identifying unique flights...")
    arcpy.SetProgressorPosition()
    arcpy.management.CopyFeatures(outputWaypoints, "temp5")      
    arcpy.management.DeleteIdentical("temp5", "flight_id")     
    totalFlights_agl = int(arcpy.management.GetCount("temp5").getOutput(0))       
    arcpy.management.CopyFeatures("temp4", "temp6")      
    arcpy.management.DeleteIdentical("temp6", "flight_id")     
    totalFlights_msl = int(arcpy.management.GetCount("temp6").getOutput(0))       
    print("Unique flights identified and counted.")    
    arcpy.AddMessage("Unique flights identified and counted.")    

    # Create and disassemble dictionaries to form AGL and MSL reclassification tables
    arcpy.SetProgressorLabel("Creating dictionaries to form reclassification tables...")
    arcpy.SetProgressorPosition()   
    aglDct = {}
    for i in range(0, aglClasses):
        aglDct[int(aglMin) + int(aglInterval) * i] = '{}'.format(i)
    agl_reclassTable = [[key, value] for key, value in aglDct.items()]
    mslDct = {}
    for i in range(0, mslClasses):
        mslDct[int(mslMin) + int(mslInterval) * i] = '{}'.format(i)
    msl_reclassTable = [[key, value] for key, value in mslDct.items()]
    print("Reclassification tables constructed.")    
    arcpy.AddMessage("Reclassification tables constructed.")        
      
    # Reclassify merged waypoints
    arcpy.SetProgressorLabel("Reclassifying waypoints by AGL and MSL altitude bands...")
    arcpy.SetProgressorPosition()    
    arcpy.management.ReclassifyField("temp3", "alt_agl", "MANUAL", "", "", "", agl_reclassTable, "", "alt_agl_MANUAL")
    arcpy.management.ReclassifyField("temp4", "alt_msl", "MANUAL", "", "", "", msl_reclassTable, "", "alt_msl_MANUAL")   
    print("Reclassification complete.")    
    arcpy.AddMessage("Reclassification complete.")
    
    # Summarize waypoint altitudes and write output to two new tables
    arcpy.SetProgressorLabel("Calculating altitude frequencies and percentages...")
    arcpy.SetProgressorPosition()
    arcpy.analysis.Frequency("temp3", "temp7", ["alt_agl_MANUAL_RANGE", "alt_agl_MANUAL"])
    totalWaypoints_agl = int(arcpy.management.GetCount("temp3").getOutput(0))
    arcpy.analysis.Frequency("temp4", "temp8", ["alt_msl_MANUAL_RANGE", "alt_msl_MANUAL"])   
    totalWaypoints_msl = int(arcpy.management.GetCount("temp4").getOutput(0))
    arcpy.management.AddField("temp7", "PERCENTAGE", "DOUBLE")
    arcpy.management.AddField("temp8", "PERCENTAGE", "DOUBLE")
    with arcpy.da.UpdateCursor("temp7", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints_agl * 100, 1)])                      
    arcpy.management.Sort("temp7", parkName + "_" + "WaypointSummary_AGL", "alt_agl_MANUAL") 
    with arcpy.da.UpdateCursor("temp8", ("FREQUENCY", "PERCENTAGE")) as cursor:
        for frequency, percentage in cursor:            
            cursor.updateRow([frequency, round(frequency / totalWaypoints_msl * 100, 1)])                        
    arcpy.management.Sort("temp8", parkName + "_" + "WaypointSummary_MSL", "alt_msl_MANUAL")
    print("Waypoint frequencies and percentages calculated.") 
    arcpy.AddMessage("Waypoint frequencies and percentages calculated.")
        
    # Report final aircraft summaries
    arcpy.SetProgressorLabel("Preparing summary messages...")
    arcpy.SetProgressorPosition()
    print("Success... Aircraft waypoint altitudes summarized!")
    arcpy.AddMessage("Success... Aircraft waypoint altitudes summarized!")
    print("AGL summary includes {0} waypoints from {1} flights.".format(totalWaypoints_agl, totalFlights_agl))
    arcpy.AddMessage("AGL summary includes {0} waypoints from {1} flights.".format(totalWaypoints_agl, totalFlights_agl))
    print("MSL summary includes {0} waypoints from {1} flights.".format(totalWaypoints_msl, totalFlights_msl))
    arcpy.AddMessage("MSL summary includes {0} waypoints from {1} flights.".format(totalWaypoints_msl, totalFlights_msl))

    # Calculate kernel density grids for each AGL altitude band
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
        
        # Specify start and end values for altitude classes and produce kernel density grids
        arcpy.SetProgressorLabel("Calculating kernel density for each AGL altitude band...")
        arcpy.SetProgressorPosition()        
        for i in range(0, aglClasses):
            aglEnd = int(aglMin) + i * int(aglInterval)
            aglStart = i * int(aglInterval)
            selRecs = arcpy.management.SelectLayerByAttribute("temp3", "NEW_SELECTION", """ {0} > {1} AND {0} <= {2}""".format(arcpy.AddFieldDelimiters("temp3", "alt_agl"), aglStart, aglEnd))
            outKernel = arcpy.sa.KernelDensity(selRecs, "", "", "", "SQUARE_KILOMETERS", "", "GEODESIC")            
            outKernel.save(parkName + "_" + "KernelDensity" + "_" + str(aglStart) + "_" + str(aglEnd))
            print("Kernel density for {0} to {1} feet AGL calculated.".format(str(aglStart), str(aglEnd)))
            arcpy.AddMessage("Kernel density for {0} to {1} feet AGL calculated.".format(str(aglStart), str(aglEnd)))
        
        # Report final kernel density summaries and check in Spatial Analyst extension
        arcpy.SetProgressorLabel("Preparing final summary messages...")
        arcpy.SetProgressorPosition()
        print("Success... AGL kernel density rasters created!")
        arcpy.AddMessage("Success... AGL kernel density rasters created!")
        arcpy.CheckInExtension("Spatial")
         
    else:
        arcpy.Warning("An ArcGIS Spatial Analyst extension is required!  The current status of this extension is {0}.".format(arcpy.CheckExtension("Spatial")))

    # Optional Processing - Calculate Band Collection Statistics to produce correlation matrix table 
    # Check to make sure optional outputTable path does not include spaces (required by text output)
    if outputTable:
        fullOutputTable = os.path.abspath(outputTable)
        spaceCheck = " " in fullOutputTable
        if spaceCheck:
            raise WhitespaceError
        else:
            pass
    else:
        pass
    # Calculate band statistics to produce correlation and covariance tables
    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            arcpy.SetProgressorLabel("Preparing band collection statistics...")
            arcpy.SetProgressorPosition()
            kernelList = arcpy.ListRasters("*" + "KernelDensity" + "*")
            arcpy.sa.BandCollectionStats(kernelList, outputTable, "DETAILED")        
            print("Success... Band collection stats calculated!")
            arcpy.AddMessage("Success... Band collection stats calculated!")
            arcpy.CheckInExtension("Spatial")
        else:
            arcpy.Warning("An ArcGIS Spatial Analyst extension is required!  The current status of this extension is {0}.".format(arcpy.CheckExtension("Spatial")))         
    except:
        pass # No value provided for the optional parameter outputTable
           
except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddError("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))

except WhitespaceError:
    print("Band collection statistics could not be produced...there is a space in the output path {0}.".format(outputTable))
    arcpy.AddWarning("Band collection statistics could not be produced...there is a space in the output path {0}.".format(outputTable))

except:
    print("An unexpected error occurred processing the input file {0}".format(inputWaypoints))
    arcpy.AddWarning("An unexpected error occurred processing the input file {0}".format(inputWaypoints))

finally:
        # Delete files no longer needed    
    arcpy.SetProgressorLabel("Finalizing messages and removing temporary files...")
    arcpy.SetProgressorPosition()
    # Delete files no longer needed
    delList = arcpy.ListFeatureClasses("temp*")    
    for i in delList:
        arcpy.management.Delete(i)
    delList = arcpy.ListTables("temp*")
    for i in delList:
        arcpy.management.Delete(i)        

    # Report execution time
    end = time.time()
    print("Total Execution Time (secs) = {0}".format(round(end - start, 1)))
    arcpy.AddMessage("Total Execution Time (secs) = {0}".format(round(end - start, 1)))
    
    # Reset the progressor
    arcpy.ResetProgressor()
    
