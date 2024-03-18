# ISS Tracker

## Overview
The ISS Tracker project provides a flask app for retrieving, processing, and analyzing International Space Station (ISS) trajectory data and current location. The primary script, iss_tracker.py, fetches ISS data from NASA's website [1], processes it into a structured format, and outputs timestamps, state vectors, speed, and/or geolocation depending on the URL used. Additionally, the project includes a unit testing script, test_iss_tracker.py, for testing the functionality of each individual function in the primary script. This allows for one to easily gain access to Epoch data in certain timeframes and can aid with identifying the positional history of the space station along with its current position, which can help with performing station observation.

## Folder Contents

- **iss_tracker.py**: Python3 app script for fetching ISS data, processing it, performing calculations, and producing outputs depending on the given URL route.
- **test_iss_tracker.py**: Unit testing script containing test cases for each route in iss_tracker.py.
- **README.md**: Instructions and information about the project.
- **Dockerfile**: Dockerfile for building the Docker image containing the app scripts and dependencies.
- **requirements.txt**: Dockerfile dependency, contains required modules that need to be installed when creating the image.
- **dockerfile-compose.yml**: Docker composition script used to simplify the process of spinning up the image.

## Instructions

### Running the Image

1. Clone this repository: `git clone https://github.com/ATaylor2003/ISS-Tracker` or directly copy the code from the repository
2. Using dockerfile compose file, run the below code to build the image as a background process. Ensure that ubuntu and other dependencies are installed.

    ```bash
    [user-vm]/ISS-Tracker$ docker-compose up -d

Ensure that you are in the directory with your copied files/cloned repo. 

### Obtaining Data

Data is automatically retrieved by the script from [1], which requires an internet connection.

### Running the Code

1. Run the primary script using curl
   
    ```bash
    [user-vm]/ISS-Tracker$ curl localhost:5000/[command]
These are the commands:
- /comment: Returns the 'comment' list object from the ISS data provided by [1].
- /header: Returns the 'header' dictionary object from the ISS data provided by [1].
- /metadata: Returns the 'metadata' dictionary object from the ISS data provided by [1].
- /epochs: Return entire data set
- /epochs?limit=int&offset=int: Return modified Epoch list using query parameters. Ensure the URL is in single or double quotes when you use multiple parameters.
- /epochs/&lt;epoch&gt;: Return state vectors for a specific Epoch specified by a timestamp
- /epochs/&lt;epoch&gt;/speed: Return instantaneous speed for a specific Epoch
- /epochs/&lt;epoch&gt;/location: Return latitude, longitude, altitude, and geoposition for a specific Epoch specified by a timestamp.
- /now: Return state vectors, instantaneous speed, latitude, longitude, altitude, and geoposition for the Epoch nearest in time.

2. To run the test scripts, use pytest:
   ```bash
    [user-vm]/ISS-Tracker$ python3 -m pytest
Ensure that you are either in the correct directory or that you specify the directory the code is copied into in the command line. Also ensure that the image is running when the test is performed.


### Output

- The output of the comment, header, and metadata routes are in their original format, with the header listing creation date and data originator, metadata listing information regarding the ISS and the reference frame used, and comment providing additional info regaridng the ISS and it's trajectory.
- The epochs route output depends on the primary script depends on the given command, but excluding the location and speed route, they output a timestamp in UTC, position values (x,y,z) in km, velocity values (x_dot, y_dot, z_dot) in km/s. The specific data or number of data values vary depending on the command and query parameters used.
- the speed route returns instantenous speed in km/s
- location provides altitude in km as well as latitude and longitude of the ISS relative to its position above Earth's surface. Additionally, it provides geopositional data based on wherever it is flying over at the specified timestamp that may include country name, city information, county information, etc depending on the location. If it is over the ocean, no location will be specified.
- the now route provides data (instantaneous speed, latitude, longitude, altitude, and geoposition) based on the Epoch nearest in time (UTC). The ISS data is provided in four minute increments, so minor differences are likely.

- Example:
   ```bash
    [user-vm]/ISS-Tracker$ curl localhost:5000/now
    Closest Epoch (UTC):
    Timestamp: 2024-078T15:52:00.000Z        
    Instantaneous Speed (km/s): 7.660487396940378
    Altitude (km) = 421.63586205726006       
    Latitude = 49.112070566067544
    Longitude = 105.12869747883002
    Geolocation = {'county': 'Baruunburen', 'state': 'Selenge', 'ISO3166-2-lvl4': 'MN-049', 'country': 'Mongolia', 'country_code': 'mn'}


### References
[1]: https://spotthestation.nasa.gov/trajectory_data.cfm