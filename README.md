### ads-b
# ADS-B Overflight Analysis Toolbox

A custom ArcGIS Pro toolbox with multiple Python-based geoprocessing tools to automate and simplify processing and analysis of Automatic Dependent Surveillance-Broadcast (ADS-B) for better understanding aircraft overflights of National Park Service (NPS) management units. 

[Project Overview](https://github.com/GISSAL/ads-b/blob/main/README.md#overview-of-ads-b-overflight-analysis)
[Toolbox Purpose](https://github.com/GISSAL/ads-b/blob/main/README.md#toolbox-purpose)
[Access the Current ArcGIS Pro Project File](https://github.com/GISSAL/ads-b/blob/main/README.md#access-the-current-arcgis-pro-project-file)
[Summary of Input and Output Files](https://github.com/GISSAL/ads-b/blob/main/README.md#summary-of-input-and-output-files)
[Geoprocessing Tools](https://github.com/GISSAL/ads-b/blob/main/README.md#geoprocessing-tools)
[Credits](https://github.com/GISSAL/ads-b/blob/main/README.md#credits)
[References](https://github.com/GISSAL/ads-b/blob/main/README.md#references)

## Overview of ADS-B Overflight Analysis

Monitoring low-level overflights is important for the NPS to fulfill its mission of providing public enjoyment while preserving cultural and natural resources (Miller et al., 2017), which includes understanding relationships between overflights and quality terrestrial visitor experiences (Mace et al., 2013). Overflight noise can degrade the acoustic environment (Beeco et al., 2020) which has been shown to have adverse effects on the experiences of visitors (McDonald et al., 1995). Research at Hawai‘i Volcanoes National Park, which received the most reported air tours of any national park in 2019 (Lignell, 2020), determined that visitors found it unacceptable to hear overflight noise more than once per 15-minute interval (Lawson et al., 2007). The sight of too many overflights may also experientially impact visitors (Tarrant et al., 1995). Furthermore, overflights have been shown to impact biophysical resources, such as wildlife (Shannon et al., 2016), which subsequently could also compromise the visitor experience (Prakash et al., 2019)

A relatively new technology, [Automatic Dependent Surveillance-Broadcast (ADS-B)](https://www.faa.gov/nextgen/programs/adsb/), can be used to understand overflight travel patterns (Beeco & Joyce, 2019). ADS-B technology features a radio signal that is broadcasted from aircraft for monitoring purposes which improves airspace safety and air traffic efficiency (FAA, 2018). Data, including position, velocity, and aircraft identification, are sent to other aircraft and ground stations (Duong et al., 2019). Broadcasted ADS-B data is unencrypted, publicly accessible, and can be collected using a data logger (Beeco & Joyce, 2019). 

Data logger components include antennas, software, display screen, USB dongle, 5V AC-DC regulator, 50’ AC power cable, thermal transfer pads, and a shielded aluminum enclosure (Beeco & Joyce, 2019). A terrestrial data logger with an expansive skyward exposure is effective at collecting large volumes of ADS-B data as millions of aircraft waypoints (Beeco & Joyce, 2020).

ADS-B data loggers can record latitude, longitude, a timestamp, altitude, and unique identification codes. The unique identification code can be related to data contained in the [FAA Releasable Database](https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download/) which provides additional relevant data including the aircraft tail number, type, and operator.

## Toolbox Purpose

This repository documents and points users to a downloadable ArcGIS Pro project file containing a custom ArcGIS Pro toolbox with multiple Python-based geoprocessing tools.  These tools can be used to process raw ADS-B data files recorded on site by data loggers, compute required flight-related attributes to support analysis, and create aircraft waypoint and flightline feature classes.  Additional included tools help automate merging daily waypoint and flightline files, facilitate screening of flights meeting certain criteria that may be omitted from further analysis, and generate summary statistics and analytical outputs for use in overflight reports. 

## Access the Current ArcGIS Pro Project File
https://kstate.maps.arcgis.com/home/item.html?id=5992d6c52e824b138aff1adb047a67e4

## Summary of Input and Output Files

Enter text here.

## Geoprocessing Tools

Enter text here.

### Tool #1 - Process Raw ADS-B Data Files

Enter text here.

### Tool #2 - Create Waypoint and Flightline Feature Classes

Enter text here.

### Tool #3 - Merge Daily Waypoints and Flightlines

Enter text here.

### Tool #4 - Create Screening Files

Enter text here.

### Tool #5 - Summarize Aircraft Waypoint Altitudes

Enter text here.

### Tool #6 - Summarize Aircraft Flights

Enter text here.

### Tool #7 - Summarize Aircraft Operators and Types

Enter text here.

### Tool #8 - Perform Density Analysis of Aircraft Waypoints

Enter text here.

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
