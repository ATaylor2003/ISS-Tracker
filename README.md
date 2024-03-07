# Midterm - ISS Tracker WIP

## Overview
The ISS Tracker project provides a flask app for retrieving, processing, and analyzing International Space Station (ISS) trajectory data. The primary script, iss_tracker.py, fetches ISS data from NASA's website, processes it into a structured format, and outputs timestamps, state vectors and/or speed depending on the given command. Additionally, the project includes a unit testing script, test_iss_tracker.py, for testing the functionality of each individual function in the primary script. This allows for one to easily gain access to Epoch data in certain timeframes. This can help with identifying the positional history of the space station along with its current position, which can aid with station observation.

## Folder Contents

- **iss_tracker.py**: Python3 app script for fetching ISS data, processing it, performing calculations, and producing outputs depending on the given command.
- **test_iss_tracker.py**: Unit testing script containing test cases for each function in iss_tracker.py.
- **README.md**: Instructions and information about the project.
- **Dockerfile**: Dockerfile for building the Docker image containing the app scripts and dependencies.

## Instructions

### Using the Image

1. Clone this repository: `git clone https://github.com/ATaylor2003/ATaylor-coe-332.git` or directly copy the `homework05` directory.
2. Using dockerfile, run the below code to build the image. Ensure that ubuntu and other dependencies are installed.

    ```bash
    [user-vm]/homework5$ docker build -t iss_tracker .

Ensure that you are in the directory with your copied files.

3. In order to run the image, use the code below.

    ```bash
    [user-vm]/homework5$ docker run --name "iss_tracker-app" -d -p 5000:5000 iss_tracker

### Obtaining Data

Data is automatically retrieved by the script, which requires an internet connection.

### Running the Code

1. Both the test scripts and the primary script can be run while the container is running.
3. To run the test scripts, use pytest:
   ```bash
    [user-vm]/homework5$ python3 -m pytest
Ensure that you are either in the correct directory or that you specify the directory the code is copied into in the command line.
4. Run the primary script using curl
   
    ```bash
    [user-vm]/homework5$ curl localhost:5000/[command]
These are the commands:
- /epochs: Return entire data set
- /epochs?limit=int&offset=int: Return modified Epoch list using query parameters. Ensure the URL is in single quotes ('') when you use multiple parameters.
- /epochs/&lt;epoch&gt;: Return state vectors for a specific Epoch specified by a timestamp
- /epochs/&lt;epoch&gt;/speed: Return instantaneous speed for a specific Epoch
- /now: Return state vectors and instantaneous speed for the Epoch nearest in time

### Output

The output of the primary script depends on the given command, but overall outpus a timestamp, position values (x,y,z), velocity values (x_dot, y_dot, z_dot), and instantaneous speed. The specific data or number of data values vary depending on the command used.