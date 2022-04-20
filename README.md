### ads-b
# ADS-B Overflight Analysis Toolbox

A custom ArcGIS Pro toolbox with multiple Python-based geoprocessing tools to automate and simplify processing and analysis of Automatic Dependent Surveillance-Broadcast (ADS-B) for better understanding aircraft overflights of National Park Service (NPS) management units. 

* [Overview of ADS-B Overflight Analysis](#overview-of-ads-b-overflight-analysis)
* [Toolbox Purpose](#toolbox-purpose)
* [Access the Current ArcGIS Pro Project File](#access-the-current-arcgis-pro-project-file)
* [Summary of Input and Output Files](#summary-of-input-and-output-files)
* [Geoprocessing Tools](#geoprocessing-tools)
    + [Tool #1 - Process Raw ADS-B Data Files](#tool-1---process-raw-ads-b-data-files)
    + [Tool #2 - Create Waypoint and Flightline Feature Classes](#tool-2---create-waypoint-and-flightline-feature-classes)
    + [Tool #3 - Merge Daily Waypoints and Flightlines](#tool-3---merge-daily-waypoints-and-flightlines)
    + [Tool #4 - Create Screening Features](#tool-4---create-screening-features)
    + [Tool #5 - Summarize Waypoint Altitudes](#tool-5---summarize-waypoint-altitudes)
    + [Tool #6 - Summarize Flights by Hour and Month](#tool-6---summarize-flights-by-hour-and-month)
    + [Tool #7 - Summarize Aircraft Operators and Types](#tool-7---summarize-aircraft-operators-and-types)
    + [Tool #8 - Perform Waypoint Density Analysis](#tool-8---perform-waypoint-density-analysis)
* [Credits](#credits)
* [References](#references)

## Overview of ADS-B Overflight Analysis

Monitoring low-level overflights is important for the NPS to fulfill its mission of providing public enjoyment while preserving cultural and natural resources (Miller et al., 2017), which includes understanding relationships between overflights and quality terrestrial visitor experiences (Mace et al., 2013). Overflight noise can degrade the acoustic environment (Beeco et al., 2020) which has been shown to have adverse effects on the experiences of visitors (McDonald et al., 1995). Research at Hawai‘i Volcanoes National Park, which received the most reported air tours of any national park in 2019 (Lignell, 2020), determined that visitors found it unacceptable to hear overflight noise more than once per 15-minute interval (Lawson et al., 2007). The sight of too many overflights may also experientially impact visitors (Tarrant et al., 1995). Furthermore, overflights have been shown to impact biophysical resources, such as wildlife (Shannon et al., 2016), which subsequently could also compromise the visitor experience (Prakash et al., 2019)

A relatively new technology, [Automatic Dependent Surveillance-Broadcast (ADS-B)](https://www.faa.gov/nextgen/programs/adsb/), can be used to understand overflight travel patterns (Beeco & Joyce, 2019). ADS-B technology features a radio signal that is broadcasted from aircraft for monitoring purposes which improves airspace safety and air traffic efficiency (FAA, 2018). Data, including position, velocity, and aircraft identification, are sent to other aircraft and ground stations (Duong et al., 2019). Broadcasted ADS-B data is unencrypted, publicly accessible, and can be collected using a data logger (Beeco & Joyce, 2019). 

Data logger components include antennas, software, display screen, USB dongle, 5V AC-DC regulator, 50’ AC power cable, thermal transfer pads, and a shielded aluminum enclosure (Beeco & Joyce, 2019). A terrestrial data logger with an expansive skyward exposure is effective at collecting large volumes of ADS-B data as millions of aircraft waypoints (Beeco & Joyce, 2020).

ADS-B data loggers can record latitude, longitude, a timestamp, altitude, and unique identification codes. The unique identification code can be related to data contained in the [FAA Releasable Database](https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download/) which provides additional relevant data including the aircraft tail number, type, and operator.

## Toolbox Purpose

This repository documents and points users to a downloadable ArcGIS Pro project file containing a custom ArcGIS Pro toolbox with multiple Python-based geoprocessing tools.  The parent Python script serving as the basis of each geoprocessing tool may also be accessed.  These tools can be used to process raw ADS-B data files recorded on site by data loggers, compute required flight-related attributes to support analysis, and create aircraft waypoint and flightline feature classes.  Additional included tools help automate merging daily waypoint and flightline files, facilitate screening of flights meeting certain criteria that may be omitted from further analysis, and generate summary statistics and analytical outputs for use in overflight reports. 

## Access the Current ArcGIS Pro Project File
https://kstate.maps.arcgis.com/home/item.html?id=5992d6c52e824b138aff1adb047a67e4

## Summary of Input and Output Files

Enter text here.

## Geoprocessing Tools

Each geoprocessing tool in the ADS-B Overflight Analysis Toolbox is described below and includes a tool summary, list of parameters, and associated ArcGIS license and extension requirements needed for successful tool operation.

### Tool #1 - Process Raw ADS-B Data Files

*Summary*

ArcGIS script-based tool code based upon <code>tool_1.py</code> that reads raw ADS-B data from the logger, creates unique flights, and generates output CSV for later GIS operations.  The output CSV filename uses the convention <code>ADSB_National Park Unit Code_ADS-B Acquisition Date.csv</code>.

*Parameters*

| Label                     | Explanation                                                         | Type     | Direction | Data Type |
| :------------------------ |:--------------------------------------------------------------------| :------- | :-------- | :-------- | 
| National Park Unit Code   | Four character abbreviation code for NPS unit.                      | Required | Input     | String    |
| Raw ADS-B File            | The ADS-B file downloaded from the data logger.                     | Required | Input     | File      |
| ADS-B Acquisition Date    | The ADS-B file acquisition date (YYYYMMDD).                         | Required | Input     | String    |
| Flight Duration Threshold | Maximum time between successive waypoints for a unique flight.      | Required | Input     | Long      |
| Output CSV Folder         | Folder where processed CSV file will be saved.                      | Required | Input     | Workspace |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes


### Tool #2 - Create Waypoint and Flightline Feature Classes

*Summary*

ArcGIS script-based tool code based upon <code>tool_2.py</code> that ingests ADS-B data processed with Tool #1 and produces point (aircraft waypoints) and line (aircraft flightlines) feature classes within a buffer distance of a management unit polygon and below a threshold altitude.  The buffer distance and altitude threshold values are user-defined.  The attribute table for the output aircraft flightlines has appended to it select fields and values from the FAA Releasable Database, as well as the new field 'Sinuosity'.  

Sinuosity values are calculated as the ratio of the curvilinear length of the flightline and the Eucliean distance between the first and last waypoint comprising the flightline and may be used to identify specific types of flights, including straight line paths typical of commercial aircraft and regular curvilinear paths characteristic of survey flights. 

*Parameters*

| Label                            | Explanation                                                                      | Type     | Direction | Data Type     |
| :------------------------------- |:---------------------------------------------------------------------------------| :------- | :-------- | :------------ | 
| Processed ADS-B File             | An output file produced by Tool #1 in the ADS-B Overflight Analysis Toolbox.     | Required | Input     | File          |
| Management Unit Polygon File     | A polygon feature representing the boundary of the management unit study area.   | Required | Input     | Feature Class |
| Buffer Distance                  | The distance (in miles) around the input feature(s) that will be buffered.       | Required | Input     | String        |
| Altitude (MSL) Threshold in Feet | The distance around the input features that will be buffered.                    | Required | Input     | Long          |
| Select FAA Releasable Database   | Choose a locally stored geodatabase copy of the FAA Releasable Database.         | Required | Input     | Workspace     |
| Output Workspace                 | Output geodatabase where aircraft waypoint and flightline files will be written. | Required | Input     | Workspace     |

*Licensing and Extension Information*

* Basic - Requires Spatial Analyst
* Standard - Requires Spatial Analyst
* Advanced - Requires Spatial Analyst

### Tool #3 - Merge Daily Waypoints and Flightlines

*Summary*

ArcGIS script-based tool code based upon <code>tool_3.py</code> that merges daily aircraft waypoint and flightlines feature classes into single feature classes for a desired time interval.

*Parameters*

| Label                        | Explanation                                                         | Type     | Direction | Data Type |
| :--------------------------- |:--------------------------------------------------------------------| :------- | :-------- | :-------- | 
| Input Workspace | The geodatabase workspace containing daily waypoint and flightline feature classes. | Required | Input | Workspace |
| Management Unit Polygon File | A polygon feature representing the boundary of the management unit study area. | Required | Input | Feature Class |
| Output Workspace | The geodatabase workspace where merged waypoint and flightline feature classes will be written. | Required | Input | Workspace |
| Output Merged Waypoints | The output waypoint feature class that will be written after merging two or more daily waypoint files. | Required | Output | Feature Class |
| Ouput Merged Flightlines | The output flightline feature class that will be written after merging two or more daily flighline files. | Required | Output | Feature Class |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

### Tool #4 - Create Screening Features

*Summary*

ArcGIS script-based tool code based upon <code>tool_4.py</code> that creates a waypoint and flighline feature class containing features meriting further scrutiny fo inclusion in later analyses.  User's may use screening parameters including the FAA Releasable Database attribute 'Type Registrant', minimum and maximum 'Sinuosity" value, and minimum flight path length (in miles).

*Parameters*

| Label                     | Explanation                                                         | Type     | Direction | Data Type |
| :------------------------ |:--------------------------------------------------------------------| :------- | :-------- | :-------- | 
| Input Waypoint File       | Enter text here. | Required | Input | Feature Class |
| Input Flightline File     | Enter text here. | Required | Input | Feature Class |
| Type Registrant Value     | Enter text here. | Required | Input | String |
| Sinuosity Values          | Enter text here. | Required | Input | String |
| Minimum Flight Length (miles) | Enter text here. | Required | Input | Long | 
| Output Workspace | Enter text here. | Required | Input | Workspace |
| Output Waypoints for Screening | Enter text here. | Required | Output | Feature Class |
| Output Flightlines for Screening | Enter text here. | Required | Output | Feature Class |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

### Tool #5 - Summarize Waypoint Altitudes

*Summary*

ArcGIS script-based tool code based upon <code>tool_5.py</code> that generates an output table summarizing waypoint frequencies by ten fixed 500 foot altitude bands.

*Parameters*

| Label                     | Explanation                                                         | Type     | Direction | Data Type     |   
| :------------------------ |:--------------------------------------------------------------------| :------- | :-------- | :------------ | 
| Parameter 1               | Merged waypoints file produced by Tool #3                           | Required | Input     | Feature Class |
| Parameter 2               | The geodatabase workspace where the summary table will be written.  | Required | Input     | Workspace     |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

### Tool #6 - Summarize Flights by Hour and Month

*Summary*

ArcGIS script-based tool code based upon <code>tool_6.py</code> that generates an output table summarizing waypoint frequencies by hour and month.

*Parameters*

| Label                     | Explanation                                                         | Type     | Direction | Data Type |
| :------------------------ |:--------------------------------------------------------------------| :------- | :-------- | :-------- | 
| Parameter 1               |                                                                     |          |           |           |
| Parameter 2               |                                                                     |          |           |           |

*Licensing and Extension Information*

* Basic - Yes
* Standard - Yes
* Advanced - Yes

### Tool #7 - Summarize Aircraft Operators and Types

*Summary*

ArcGIS script-based tool code based upon <code>tool_7.py</code> that generates an output table summarizing flight (flightlines) by operator as reported in the FAA Releasable Database.

*Parameters*

| Label                     | Explanation                                                         | Type     | Direction | Data Type |
| :------------------------ |:--------------------------------------------------------------------| :------- | :-------- | :-------- | 
| Parameter 1               |                                                                     |          |           |           |
| Parameter 2               |                                                                     |          |           |           |

*Licensing and Extension Information*

* Basic - 
* Standard - 
* Advanced - 

### Tool #8 - Perform Waypoint Density Analysis

*Summary*

ArcGIS script-based tool code based upon <code>tool_8.py</code> that performs a kernel density analysis of aircraft waypoints within a buffered management unit.

*Parameters*

| Label                     | Explanation                                                         | Type     | Direction | Data Type |
| :------------------------ |:--------------------------------------------------------------------| :------- | :-------- | :-------- | 
| Input Waypoint File | Enter text here. | Required | Input | Feature Class |
| Management Unit Buffer Polygon | Enter text here. | Required | Input | Feature Class |
| Output Workspace | Enter text here. | Required | Input | Workspace |
| Output Kernel Density Raster | Enter text here. | Required | Output | Raster Dataset |

*Licensing and Extension Information*

* Basic - Requires Spatial Analyst
* Standard - Requires Spatial Analyst
* Advanced - Requires Spatial Analyst

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
