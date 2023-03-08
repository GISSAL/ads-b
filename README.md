### ads-b
# ADS-B Overflight Analysis Toolbox

A custom ArcGIS Pro toolbox with multiple Python-based geoprocessing script tools to automate and simplify processing and analysis of Automatic Dependent Surveillance-Broadcast (ADS-B) data for better understanding aircraft overflights of National Park Service (NPS) management units. 

* [Overview of ADS-B Overflight Analysis](#overview-of-ads-b-overflight-analysis)
* [Toolbox Purpose](#toolbox-purpose)
* [Access the Current ArcGIS Pro Project File](#access-the-current-arcgis-pro-project-file)
* [Get Started with the Toolbox](#get-started-with-the-toolbox)
    + [Tool #1 - Process Raw ADS-B Data Files](#tool-1---process-raw-ads-b-data-files)
    + [Tool #2 - Create Waypoint and Flightline Feature Classes](#tool-2---create-waypoint-and-flightline-feature-classes)
    + [Tool #3 - Merge Daily Waypoints and Flightlines](#tool-3---merge-daily-waypoints-and-flightlines)
    + [Tool #4 - Screen Suspected Non-Tourism Flights](#tool-4---screen-suspected-non-tourism-flights)
    + [Tool #5 - Summarize Waypoint Altitudes](#tool-5---summarize-waypoint-altitudes)
    + [Tool #6 - Summarize Waypoints by Time, Operator, and Type](#tool-6---summarize-waypoints-by-time-operator-and-type)
* [Credits](#credits)
* [References](#references)

## Overview of ADS-B Overflight Analysis

Monitoring low-level overflights is important for the NPS to fulfill its mission of providing public enjoyment while preserving cultural and natural resources (Miller et al., 2017), which includes understanding relationships between overflights and quality terrestrial visitor experiences (Mace et al., 2013). Overflight noise can degrade the acoustic environment (Beeco et al., 2020) which has been shown to have adverse effects on the experiences of visitors (McDonald et al., 1995). Research at Hawai‘i Volcanoes National Park, which received the most reported air tours of any national park in 2019 (Lignell, 2020), determined that visitors found it unacceptable to hear overflight noise more than once per 15-minute interval (Lawson et al., 2007). The sight of too many overflights may also experientially impact visitors (Tarrant et al., 1995). Furthermore, overflights have been shown to impact biophysical resources, such as wildlife (Shannon et al., 2016), which subsequently could also compromise the visitor experience (Prakash et al., 2019)

A relatively new technology, [Automatic Dependent Surveillance-Broadcast (ADS-B)](https://www.faa.gov/nextgen/programs/adsb/), can be used to understand overflight travel patterns (Beeco & Joyce, 2019). ADS-B technology features a radio signal that is broadcasted from aircraft for monitoring purposes which improves airspace safety and air traffic efficiency (FAA, 2018). Data, including position, velocity, and aircraft identification, are sent to other aircraft and ground stations (Duong et al., 2019). Broadcasted ADS-B data is unencrypted, publicly accessible, and can be collected using a data logger (Beeco & Joyce, 2019). 

Data logger components include antennas, software, display screen, USB dongle, 5V AC-DC regulator, 50’ AC power cable, thermal transfer pads, and a shielded aluminum enclosure (Beeco & Joyce, 2019). A terrestrial data logger with an expansive skyward exposure is effective at collecting large volumes of ADS-B data as millions of aircraft waypoints (Beeco & Joyce, 2020).

ADS-B data loggers can record latitude, longitude, a timestamp, altitude, and unique identification codes. The unique identification code can be related to data contained in the [FAA Releasable Database](https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download/) which provides additional relevant data including the aircraft tail number, type, and operator.

## Toolbox Purpose

This repository documents and points users to a downloadable ArcGIS Pro project package containing a custom ArcGIS Pro toolbox with multiple Python-based geoprocessing script tools.  The parent Python script serving as the basis of each geoprocessing tool may also be accessed.  These tools can be used to process raw ADS-B data files recorded on site by data loggers, create aircraft waypoint and flightline feature classes, and compute required flight-related attributes to support a variety of analyses.  Additional tools help automate merging daily waypoint and flightline files, facilitate screening of flights meeting certain criteria that may be omitted from further analysis, and generate summary statistics and analytical outputs for use in aircraft overflight reporting. 

## Access the Current ArcGIS Pro Project File from the K-State GIS Portal
[https://arcg.is/1vLjHu](https://arcg.is/1vLjHu)

## Get Started with the Toolbox

Each geoprocessing tool in the ADS-B Overflight Analysis Toolbox is described below and includes a tool summary, dependencies, list of parameters, associated ArcGIS license and extension requirements needed for successful tool operation, and a description section containing details about the processing steps completed.

Before starting, be sure to have an ArcGIS Pro project file created with these additional features:

* Add a folder connection to a system folder containing raw ADS-B data files in TSV format (e.g., InputData).
* Create and add a folder connection to another system folder that will store the CSV outputs from Tool #1 (e.g., OutputData).
* Add a file or enterprise geodatabase to your project containing, at minimum, study area specific files for the management unit boundary and digital elevation model that records elevation in units of meters.
* Add a file or enterprise geodatabase to your project that contains, at minimum, two tables imported from the FAA Releasable Database.  The required tables are MASTER and ACFTREF.  A compressed file containing text-based attribute tables valid for a calendar year can be downloaded from https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download/.
* Finally, download the ADS-B Overflight Analysis Toolbox from this site and add it to your ArcGIS Pro project.  The tools in the toolbox contain embedded versions of the scripts that are also hosted in this repository.

Tools in the ADS-B Overflight Analysis Toolbox provide several checks that remove records from further analysis.  Users may need to modify these procedures to better suit particular needs.  Filtering operations are outlined in the Description section for each tool and highlighted in **bold** text.

### Tool #1 - Process Raw ADS-B Data Files

*Summary*

Reads raw ADS-B data collected from a logger, performs basic structural checks on each file, formats fields to ensure proper data types, removes flights not meeting a 1-2 second time since last communication (TSLC), identifies and creates unique flights based on a user-defined elapsed time between sequential aircraft waypoints, and generates output CSV files for later ADS-B GIS operations.  The output CSV filename uses the convention <code>ADSB_National Park Unit Code_ADS-B Acquisition Date.csv</code> where the acquisition date is obtained from the input TSV file.  

*Dependencies*

Requires access to the Python script <code>ads_b_tool_1.py</code> and raw ADS-B data logger files. 

*Parameters*

| Label                     | Explanation                                                         | Type     | Direction | Data Type | 
| :------------------------ | :-------------------------------------------------------------------| :------- | :-------- | :-------- | 
| National Park Unit Code   | Enter the four letter park unit code (e.g., GRSM, HAVO) where the ADS-B data was collected.  For management units operating more than one                               data logger, it is recommended to also include a short name for the logger location (e.g., GRSM_COVEMTN or GRSM_ELKMONT). | Required | Input     | String    |
| Raw ADS-B File            | Select a single ADS-B TSV data logger file.  This tool can also be operated in "batch" mode to process multiple input files in a single tool run.                    | Required | Input     | File      |
| Flight Duration Threshold (secs) | Enter a duration threshold (in seconds) that defines the minimum time between successive aircraft waypoints that must pass before a new flight by that aircraft is considered to occur.      | Required | Input     | Long      |
| Output CSV Folder         | Select a folder workspace where where the output CSV file will be saved. | Required | Input     | Workspace |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

*Description*

Ingests and pre-processes a single daily ADS-B data logger TSV file and returns a new output daily file in CSV format for use in later ADS-B GIS data processing.  This tool can be operated in "batch" mode within ArcGIS Pro to process several daily ADS-B TSV files in a single tool run.  Tool messaging includes data regarding QA/QC results, number of unique aircraft and flights, and total tool execution time.  Key processing steps include:
* Checks for presence of required header line and exits with an appropriate error message if it is not present.  Other structural errors are also trapped and an error message reported.
* Effectively reads logger data files that have recorded data using different field names for the same variable (e.g., TIME vs. timestamp).
* Unpacking validFlags data from the ADS-B input file and removing any records with invalid latitude, longitude, and/or altitude flags.
* **Removes any records with Time Since Last Communication (TSLC) values equal to 0 or greater than or equal to 3 (i.e., only TSLC values of 1 or 2 are retained).**  
* Converts original Unix timestamps to Python datetime objects in UTC which are then re-scaled to integer values.
* Calculates the time difference between sequential waypoints for each unique aircraft.
* **Removes any identical waypoints in a single daily file that have the same values for aircraft ICAO address, time, latitude, and longitude.**
* Appends a zero-based index to the existing ICAO Address to create a new *FlightID* attribute and values (e.g., ICAO_0, ICAO_1, etc).  A new flight by the same aircraft is indicated when two sequential waypoints have a time difference exceeding the user-defined parameter *Flight Duration Threshold (secs)* which is set to a default value of 900 seconds.
* **Removes any record where a unique flight_id has just a single recorded waypoint.** 

### Tool #2 - Create Waypoint and Flightline Feature Classes

*Summary*

Ingests ADS-B data processed with **Tool #1 - Process Raw ADS-B Files** and produces point (aircraft waypoint) and line (aircraft flightline) feature classes for all features within a user-defined distance of a management unit polygon and below a user-defined altitude threshold.  The attribute table for the output aircraft flightlines has appended to it select fields and values from the **FAA Releasable Database**, as well as the new field *Sinuosity* which may be useful in identifying specific types of flights, including straight line paths typical of commercial aircraft and regular curvilinear paths characteristic of survey flights. 

*Dependencies*

Requires access to the Python script <code>ads_b_tool_2.py</code> and uses as input the output from **Tool #1 - Process Raw ADS-B Data Files**. 

*Parameters*

| Label                            | Explanation                                                                      | Type     | Direction | Data Type     |
| :------------------------------- |:---------------------------------------------------------------------------------| :------- | :-------- | :------------ | 
| Processed ADS-B File | Select a processed ADS-B CSV file generated by **Tool #1 - Process Raw ADS-B Files**. | Required | Input | File |
| Management Unit Polygon File | Select a polygon feature class representing the boundary of the management unit study area.   | Required | Input | Feature Class |
| Buffer Distance | Enter a horizontal buffer distance (in miles) within which aircraft waypoints will be processed. | Required | Input | String |
| MSL Altitude Threshold (feet) | Enter a MSL altitude value (in feet) above which flights will be excluded from further analysis. | Required | Input | Long |
| Input DEM | Select a digital elevation model (DEM) for the management unit. | Required | Input | Raster Dataset|
| FAA Releasable Database | Select the local geodatabase containing recent versions of the FAA Releasable Database tables MASTER and ACFTREF. | Required | Input | Workspace |
| Output Workspace | Choose an output geodatabase workspace to store output daily aircraft waypoint and flightline feature classes. | Required | Input | Workspace |

*Licensing and Extension Information*

* Basic - Requires Spatial Analyst
* Standard - Requires Spatial Analyst
* Advanced - Requires Spatial Analyst

*Description*

Ingests preprocessed ADS-B CSV files produced by **Tool #1 - Process Raw ADS-B Files** and creates point (aircraft waypoints) and line (aircraft flightlines) feature classes in an existing geodatabase workspace.  Aircraft data located beyond user-defined horizontal (distance in miles) and vertical buffers (MSL altitude in feet) are excluded from the output.  Tool messaging includes the number of waypoints and flightlines in each output feature class, the number of aircraft with a "null" value for N Number, and total tool execution time. Key processing steps include:
* **Creates a buffer file for the management unit polygon feature class based on a user-defined distance and excludes any waypoints outside the buffer from further analysis**.
* Checks to make sure aircraft waypoints exist within a buffered management unit boundary before proceeding and exits if none are present.
* Converts original MSL altitudes in the aircraft waypoints table from units of meters to feet.
* Calculates a new *Alt_AGL* field (altitude above ground level) in the aircraft waypoints table with values based on aircraft waypoint MSL altitudes minus corresponding terrain elevations from the user-supplied digital elevation model (DEM).
* Adds new fields and values for the aircraft flightlines feature class including *ICAO Address* (retrieved from the aircraft waypoint table), *Sinuosity* , and *LengthMiles*. *Sinuosity* is calculated as the ratio of the curvilinear length of the flightline and the Eucliean distance between the first and last waypoint comprising the flightline and may be useful in identifying specific types of flights, including straight line paths typical of commercial aircraft and regular curvilinear paths characteristic of survey flights. The field *LengthMiles* is the total length of the flightpath in miles.
* **Removes any aircraft flightline features with a length of 0.**
* Performs a table join between aircraft flightlines and select fields from the FAA Releasable Database.  Joined fields from the MASTER table include N-Number, MFR MDL CODE, TYPE REGISTRANT, NAME, and Type Engine.  A single field – Model – is joined from the ACFTREF table.  Users must create a local geodatabase (e.g., FAA_Releasable_Database.gdb),  download current copies of the MASTER and ACFTREF tables from the FAA Releasable Database website (https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download), then import the tables into the local geodatabase for this join operation to be successful.

### Tool #3 - Merge Daily Waypoints and Flightlines

*Summary*

Merges all daily aircraft waypoint and flightlines feature classes in a user-defined workspace into single point and line feature classes.

*Dependencies*

Requires access to the Python script <code>ads_b_tool_3.py</code> and uses as input the output from **Tool #2 - Create Waypoint and Flightline Feature Classes**. 

*Parameters*

| Label                        | Explanation                                                         | Type     | Direction | Data Type |
| :--------------------------- |:--------------------------------------------------------------------| :------- | :-------- | :-------- | 
| Input Workspace | Select the geodatabase workspace containing daily waypoint and flightline feature classes produced by **Tool #2 - Create Waypoint and Flightline Feature Classes**. Caution - All point and line features this workspace will be merged. | Required | Input | Workspace |
| Output Merged Waypoints | Enter a name for the merged aircraft waypoint feature class. | Required | Output | Feature Class |
| Ouput Merged Flightlines | Enter a name for the merged aircraft flightline feature class. | Required | Output | Feature Class |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

*Description*

Merges all daily aircraft waypoint and flightline feature classes stored in the user-defined workspace into single point and line feature classes.  Waypoints are further filtered to identify and remove any duplicates which may be introduced when combining daily waypoint feature classes created from data recorded at two or more data loggers within the management unit.  Tool messaging includes the number of original, duplicate, and final waypoints and the total number of unique aircraft flightlines in the merged aircraft waypoint and flightline feature classes, respectively.  Key processing steps include:
* Creates a temporary new field called *DATE* based on the original datetime stamp field *TIME*, but including only the yyyyMMdd information.  The newly created *DATE* field is deleted at the end of the script after it is no longer needed.
* Combines all point and line feature classes present in the user-defined input workspace into single merged waypoint and flightline feature classes.
* **Removes duplicate waypoints from the merged feature class if identical values appear in the *flight_id*, *lat*, *lon*, and *DATE8 fields.**

### Tool #4 - Screen Suspected Non-Tourism Flights

*Summary*

Creates a waypoint and flightline feature class containing features suspected of being unrelated to management unit tourism operations based on screening parameters including the FAA Releasable Database attribute *Type Registrant*, minimum and maximum *Sinuosity* values, and a minimum flight path length (in miles).  The tool also automatically removes these suspect waypoints and flightlines from the existing merged feature classes produced by **Tool #3 - Merge Daily Waypoints and Flightlines** and creates new and "cleaned" merged waypoint and flightline feature classes.

*Dependencies*

Requires access to the Python script <code>ads_b_tool_4.py</code> and uses as input the output from **Tool #3 - Merge Daily Waypoints and Flightlines**. 

*Parameters*

| Label                     | Explanation                                                         | Type     | Direction | Data Type |
| :------------------------ |:--------------------------------------------------------------------| :------- | :-------- | :-------- | 
| Input Waypoint File | Select the merged waypoint feature class produced by **Tool #3 - Merge Daily Waypoints and Flightlines**. | Required | Input | Feature Class |
| Input Flightlines File | Select the merged flightline feature class produced by **Tool #3 - Merge Daily Waypoints and Flightlines**. | Required | Input | Feature Class |
| Type Registrant Value(s) | Enter a single or comma-separated list of values representing aircraft registrant types from the **FAA Releasable Database** that should be eliminated from further analysis.  Valid values include:  1 = Individual; 2 = Partnership; 3 = Corporation; 4 = Co-Owned; 5 = Government; 7 = LLC; 8 = Non-Citizen Corporation; 9 = Non-Citizen Co-Owned.. | Required | Input | String |
| Sinuosity Value(s) | Enter a comma-separated list of values for the minimum and maximum sinuosity below or above which flightlines should be eliminated from further analysis (e.g., 0.10, 0.99).  For reference, a sinuosity value of 1 equals a straight line. | Required | Input | String |
| Aircraft Operator Name(s) | Enter comma-separated values for aircraft operator names (e.g., AMERICAN AIRLINES INC, DELTA AIR LINES INC) to identify flights for further scrutiny.  Note that operator names must exactly match those published in the FAA Releasable Database. | Required | Input | String |
| Minimum Flight Length (miles) | Enter the minimum flightpath length (in miles) below which flightlines will be eliminated from further analysis.  For example, if a value of 1 is entered, flightlines with a total flight length less than 1 mile will be excluded. | Required | Input | Long |
| Output Suspect Waypoints | Enter a name for the output point feature class containing waypoints for further scrutiny. | Required | Output | Feature Class |
| Output Suspect Flightlines | Enter a name for the output line feature class containing flightlines for further scrutiny. | Required | Output | Feature Class |
| Output Screened Waypoints | Enter a name for the "cleaned" output point feature class with suspect aircraft waypoints removed. | Required | Output | Feature Class |
| Output Screened Flightlines | Enter a name for the "cleaned" output line feature class with suspect aircraft flightlines removed. | Required | Output | Feature Class |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

*Description*

The output of this tool includes waypoints/flights that meet certain characteristics typical of flights that should be omitted from further overflight analyses.  One example of this might be commerical airliner flights included in the parameter *Aircraft Operator Name(s)*. The tool also automatically deletes suspect flights from the existing merged waypoint and flightline feature classes and creates "clean" versions of both.  Key considerations when running this tool include:
* **For the parameter *Type Registrant Values*, users should enter one or more comma-separated numeric values representing valid values from the *Type Registrant* field in the FAA Releasable Database (e.g., 5 = Government)**.
* **For the parameter *Sinuosity Values*, users should enter a comma-separated minimum and maximum sinuosity value to select flightlines with less than the minimum or greater than the maximum for identifying suspect flights (e.g., 0.10, 0.99)**.
* **For the parameter *Aircraft Operator Name(s)*, users should enter comma-separated values for aircraft operator names (e.g., AMERICAN AIRLINES INC, DELTA AIR LINES INC) to select specific operators of suspect flights.  Note that operator names must exactly match those published in the FAA Releasable Database**.

### Tool #5 - Summarize Waypoint Altitudes

*Summary*

Creates a new output point feature class that removes waypoints outside a more restrictive buffer distance, kernel density rasters for waypoints occurring within ten user-defined AGL altitude bands, and output tables that summarize waypoint frequencies by both AGL and MSL altitude bands.

*Dependencies*

Requires access to the Python script <code>ads_b_tool_5.py</code> and uses as input the output from **Tool #4 - Screen Suspected Non-Tourism Flights**. 

*Parameters*

| Label                        | Explanation                                                         | Type     | Direction | Data Type     |
| :--------------------------- |:--------------------------------------------------------------------| :------- | :-------- | :------------ | 
| National Park Unit Code | Enter the four letter park unit code (e.g., GRSM, HAVO) where the ADS-B data was collected. | Required | Input | String |
| Input Waypoint File | Select the screened merged waypoints feature class produced by **Tool #4 - Screen Suspected Non-Tourism Flights**. | Required | Input | Feature Class |
| Management Unit Polygon File | Select a polygon feature class representing the boundary of the management unit study area. | Required | Input | Feature Class |
| Buffer Distance (miles) | Enter a horizontal buffer distance (in miles) within which aircraft waypoints will be processed.  | Required  | Input | String |
| Minimum AGL Altitude | Enter the maximum AGL altitude value for the first (lowest altitude) class. | Required | Input | Long |
| Maximum AGL Altitude | Enter the maximum AGL altitude value for the last (highest altitude) class. | Required | Input | Long |
| AGL Altitude Interval | Enter the AGL altitude interval to use in a ten-class classification. | Required | Input | Long |
| Minimum MSL Altitude | Enter the maximum MSL altitude value for the first (lowest altitude) class.  | Required | Input | Long |
| Maximum MSL Altitude | Enter the maximum MSL altitude value for the last (highest altitude) class. | Required | Input | Long |
| MSL Altitude Interval | Enter the MSL altitude interval to use in a ten-class classification. | Required | Input | Long |
| Output Waypoint File | Enter a name for the output point feature class containing waypoints used in the altitude summary. | Required | Output | Feature Class |
| Output Band Statistics Table | Enter a name for the output ASCII file containing detailed statistics from the kernel density rasters. | Optional | Output | Text File |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

*Description*

Produces a new waypoint feature class after a more restrictive buffer operation and two output tables that include the frequency and percentage of total waypoints by user-defined altitude bands.  One table reports altitudes above mean sea level (WaypointSummary_MSL) and the other based on altitudes above ground level (WaypointSummary_AGL).  The user-supplied altitude band information is also used to produce a total of ten AGL kernel density rasters to assist with visualization.  Key processing steps include:
* **A new buffer is created and used to clip the input screened waypoints file by a more restrictive distance than used in Tool #2 - Create Waypoint and Flightline Feature Classes**.
* Waypoint altitudes (in both units of AGL and MSL) are reclassified according to user-defined values for the maximum altitude of the first altitude class, the maximum value of the last altitude class, and the desired altitude interval.
* Summary tables are produced that include the frequency and percentage of total waypoints within each AGL and MSL altitude band. The national park unit code provided by the user is appended to the beginning of the names for both of these tables which will appear automatically in the same output workspace used for the *Output AGL Waypoint File*.
* A series of ten kernel density rasters are produced for each AGL altitude band to assist with visualization of overflights.

### Tool #6 - Summarize Waypoints by Time, Operator, and Type

*Summary*

Generates six output tables summarizing waypoint frequencies by hour, day of week, weekday vs. weekend, month, aircraft operator (e.g., individual, corporation), and aircraft type (e.g., fixed wing single engine, rotorcraft) using as input the same waypoints summarized by altitude bands in **Tool #5 - Summarize Waypoint Altitudes**. 

*Dependencies*

Requires access to the Python script <code>ads_b_tool_6.py</code> and uses as input the output from **Tool #5 - Summarize Waypoint Altitudes**. 

*Parameters*

| Label                        | Explanation                                                         | Type     | Direction | Data Type     |
| :--------------------------- |:--------------------------------------------------------------------| :------- | :-------- | :------------ | 
| National Park Unit Code | Enter the four letter park unit code (e.g., GRSM, HAVO) where the ADS-B data was collected. | Required | Input | String |
| Input Waypoint File | Enter the point feature class produced by **Tool #5 - Summarize Waypoint Altitudes** and containing the waypoints used in previous altitude  summary. | Required | Input | Feature Class |
| FAA Releasable Database | Select the local geodatabase containing recent versions of the FAA Releasable Database tables MASTER and ACFTREF. | Required | Input | Workspace |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

Produces six output tables that include the frequency and percentage of total flights based on the hour, day of week, weekday vs. weekend, month, aircraft operator, and aircraft type using as input the output waypoint feature class produced by **Tool #5 - Summarize Waypoint Altitudes**.  Each table is written to the same workspace where the *Input Waypoint File* is located.  One table reports the hourly summary (WaypointSummary_HR) and the other the monthly summary (WaypointSummary_MO).  The national park unit code provided by the user is appended to the beginning of the names for each output table (e.g., GRSM_FlightSummary_DAY, GRSM_FlightSummary_Operators).  Key processing steps executed include:
* Flight summaries are based on the hour and time of the first waypoint for each unique flight in the input file.
* **UTC times for waypoints recorded by the ADS-B data logger are converted to local times prior to summarization**.
* **Performs a table join between aircraft flightlines and select fields from the FAA Releasable Database**.  Joined fields from the MASTER table include N-Number, MFR MDL CODE, TYPE REGISTRANT, NAME, and Type Engine.  A single field – Model – is joined from the ACFTREF table.  Users must create a local geodatabase (e.g., FAA_Releasable_Database.gdb),  download current copies of the MASTER and ACFTREF tables from the FAA Releasable Database website (https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download), then import the tables into the local geodatabase for this join operation to be successful.
* Summary tables are produced that include the frequency and percentage of total flights occurring by hour of the day, day of week, weekday vs. weekend, month of the year, aircraft operator (i.e., TYPE_REGISTRANT field from the FAA Releaseable Database), and aircraft type (i.e., TYPE_AIRCRAFT field from the FAA Releasable Database).
* Possible TYPE_REGISTRANT values include: [1, "Individual"], [2, "Partnership"], [3, "Corporation"], [4, "Co-Owned"], [5, "Government"], [7, "LLC"], [8, "Non-Citizen Corporation"], [9, "Non-Citizen Co-Owned"].
* Possible TYPE_AIRCRAFT values include:  [1, "Glider"], [2, "Balloon"], [3, "Blimp/Dirigible"], [4, "Fixed Wing Single Engine"], [5, "Fixed Wing Multi Engine"], [6, "Rotorcraft"], [7, "Weight-Shift-Control"], [8, "Powered Parachute"], [9, "Gyroplane"]

## Credits

[Applied Park Science Laboratory](https://kstateapslab.wixsite.com/appliedparkscience) and [Geographic Information Systems Spatial Analysis Laboratory](https://www.ksu.edu/gissal), Kansas State University

## References

Beeco, J. A., & Joyce, D. (2019). Automated aircraft tracking for park and landscape planning. Landscape and Urban Planning, 186, 103-111.

Beeco, J. A., Joyce, D., & Anderson, S. (2020). Evaluating the use of spatiotemporal aircraft data for air tour management planning and compliance. Journal of Park and Recreation Administration. doi:10.18666/JPRA-2020-10341

Duong, Q., Tran, T., Pham, D. T., & Mai, A. (2019, March). A Simplified Framework for Air Route Clustering Based on ADS-B Data. In 2019 IEEE-RIVF International Conference on Computing and Communication Technologies (RIVF) (pp. 1-6). IEEE.

FAA (2018). ADS-B, Research, Airspace. Retrieved from: https://www.faa.gov/nextgen/equipadsb/research/airspace/

Lawson, S., K Hockett, B. Kiser, N. Reigner, A. Ingrm, J. Howard, and S. Dymond (2007).  Social Science Research to Inform Soundscape Management in Hawai‘i Volcanoes
National Park. Final Report. Department of Forestry, College of Natural Resources, Virginia Polytechnic Institute and State University.

Lignell, B. W. (2020). Reporting information for commercial air tour operations over units of the national park system: 2019 annual report. Natural Resource Report NPS/NRSS/NSNSD/NRR— 2020/2193. National Park Service, Fort Collins, Colorado.

Mace, B. L., Corser, G. C., Zitting, L., & Denison, J. (2013). Effects of overflights on the national park experience. Journal of Environmental Psychology, 35, 30-39.

McDonald, C. D., Baumgarten, R. M., & Iachan, R. (1995). Aircraft management studies: National park service visitors survey. HMMH Report, (290940.12), 94-2.

Miller, Z. D., Fefer, J. P., Kraja, A., Lash, B., & Freimund, W. (2017, January). Perspectives on visitor use management in the National Parks. In The George Wright Forum (Vol. 34, No. 1, pp. 37-44). George Wright Society.

Prakash, S. L., Perera, P., Newsome, D., Kusuminda, T., & Walker, O. (2019). Reasons for visitor dissatisfaction with wildlife tourism experiences at highly visited national parks in Sri Lanka. Journal of Outdoor Recreation and Tourism, 25, 102-112.

Shannon, G., McKenna, M. F., Angeloni, L. M., Crooks, K. R., Fristrup, K. M., Brown, E., Warner, K. A., Nelson, M. D., White, C., Briggs, J., McFarland, S., & Wittenmyer, G. (2016). A synthesis of two decades of research documenting the effects of noise on wildlife. Biological Reviews, 91(4), 982-1005.

Tarrant, M. A., Haas, G. E., & Manfredo, M. J. (1995). Factors affecting visitor evaluations of aircraft overflights of wilderness areas. Society & Natural Resources, 8(4), 351-360.
