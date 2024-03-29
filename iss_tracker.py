import requests
import xmltodict
import math
import pytz
from datetime import datetime
import logging
from typing import List, Dict, Any
from flask import Flask, request
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
data_off = 3
# Function to fetch ISS data from NASA's website and parse it into a list of dictionaries
def fetch_iss_data() -> List[Dict[str, Any]]:
    """
    Fetches ISS data from NASA's website and parses it into a list of dictionaries.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing ISS data.
    """
    try:
        # Fetch XML data from the website
        response = requests.get("https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml")
        response.raise_for_status()  # Raise exception for non-200 status codes
        # Parse XML data into a dictionary
        data_dict = xmltodict.parse(response.content)

        # Extract state vectors
        state_vectors = data_dict['ndm']['oem']['body']['segment']['data']['stateVector']

        #Extract comments
        comments = data_dict['ndm']['oem']['body']['segment']['data'].get('COMMENT', [])
        if not isinstance(comments, list):
            comments = [comments]

        header = data_dict['ndm']['oem']['header']
        if not isinstance(header, list):
            header = [header]

        metadata = data_dict['ndm']['oem']['body']['segment']['metadata']
        if not isinstance(metadata, list):
            metadata = [metadata]
        
        # Initialize the ISS data list
        iss_data = []
        iss_data.append({'comments': comments})
        iss_data.append({'header': header})
        iss_data.append({'metadata': metadata})


        # Check if state_vectors is a list, and converts if not
        if not isinstance(state_vectors, list):
            state_vectors = [state_vectors]

        # Iterate over each state vector and extract information
        for state_vector in state_vectors:
            epoch = state_vector['EPOCH']
            position = {
                'x': float(state_vector['X']['#text']),
                'y': float(state_vector['Y']['#text']),
                'z': float(state_vector['Z']['#text'])
            }
            velocity = {
                'x_dot': float(state_vector['X_DOT']['#text']),
                'y_dot': float(state_vector['Y_DOT']['#text']),
                'z_dot': float(state_vector['Z_DOT']['#text'])
            }
            iss_data.append({'state': {'timestamp': epoch, 'position': position, 'velocity': velocity}})
        return iss_data
    except Exception as e:
        logger.error(f"Error fetching or parsing ISS data: {e}")
        return []

# Get the ISS data
iss_data = fetch_iss_data()

# Function to print position and velocity data with proper formatting
def print_position_velocity_data(state: Dict[str, Any], indent: str = '') -> str:    
    """
    Formats position and velocity data into a human-readable string.

    Args:
        position (Dict[str, Any]): Dictionary containing position data.
        velocity (Dict[str, Any]): Dictionary containing velocity data.
        indent (str): String representing indentation level for formatting.

    Returns:
        str: Formatted string containing position and velocity data.
    """
    output = ""
    output += f"{indent}Position (km):\n"
    for axis, value in state['position'].items():
        output += f"{indent}   {axis} = {value}\n"
    output += f"{indent}Velocity (km/s):\n"
    for axis, value in state['velocity'].items():
        output += f"{indent}   {axis} = {value}\n"
    return output

# Route to return a modified list of epochs given query parameters (/epochs?limit=int&offset=int)
@app.route('/epochs', methods=['GET'])
def get_epochs() -> str:
    """
    Route to return a modified list of epochs based on query parameters.

    Returns:
        str: String containing formatted epoch data.
    """
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', len(iss_data)-offset-data_off))
    modified_states = iss_data[data_off+offset:data_off+offset+limit]
    output = "Epochs:\n"
    if offset >= (len(iss_data)-data_off) or offset < 0:
        logger.error({'error': 'Offset is larger than data set or negative'})
        return 'Error: Offset is larger than data set or negative\n'
    elif limit > (len(iss_data)-data_off) or limit <= 0:
        logger.error({'error': 'Limit is larger than data set or negative'})
        return 'Error: Limit is larger than data set or negative\n'
    elif limit+offset > (len(iss_data)-data_off):
        logger.error({'error': 'Limit + Offset is larger than data set'})
        return 'Error: Limit + Offset is larger than data set\n'
    
    for state_data in modified_states:
        state = state_data['state']
        output += f"Timestamp: {state['timestamp']}\n"
        output += print_position_velocity_data(state, indent='   ')
    return output

# Route to return state vectors for a specific epoch
@app.route('/epochs/<epoch>', methods=['GET'])
def get_state_vectors(epoch: str) -> str:
    """
    Route to return state vectors for a specific epoch.

    Args:
        epoch (str): Epoch timestamp.

    Returns:
        str: String containing formatted state vector data.
    """
    state_data = next((data for data in iss_data[data_off:] if data['state']['timestamp'] == epoch), None)
    if state_data:
        state = state_data['state']
        output = "State Vector:\n"
        output += f"Timestamp: {state['timestamp']}\n"
        output += print_position_velocity_data(state, indent='   ')
        return output
    else:
        logger.error({'error': 'State vector not found for the given epoch'})
        return 'Error: State vector not found for the given epoch'

# Route to return instantaneous speed for a specific epoch
@app.route('/epochs/<epoch>/speed', methods=['GET'])
def get_instantaneous_speed(epoch: str) -> str:
    """
    Route to return instantaneous speed for a specific epoch.

    Args:
        epoch (str): Epoch timestamp.

    Returns:
        str: String containing formatted instantaneous speed data.
    """
    state_data = next((data for data in iss_data[data_off:] if data['state']['timestamp'] == epoch), None)
    if state_data:
        state = state_data['state']
        velocity = state['velocity']
        instantaneous_speed = (velocity['x_dot'] ** 2 + velocity['y_dot'] ** 2 + velocity['z_dot'] ** 2) ** 0.5
        output = f"Instantaneous Speed (km/s): {instantaneous_speed}\n"
        return output
    else:
        logger.error({'error': 'State vector not found for the given epoch'})
        return 'Error: State vector not found for the given epoch'

# Route to return state vectors and instantaneous speed for the epoch nearest in time
@app.route('/now', methods=['GET'])
def get_nearest_epoch() -> str:
    """
    Route to return state vectors and instantaneous speed for the epoch nearest in time.

    Returns:
        str: String containing formatted epoch and speed data.
    """
    now = datetime.now(pytz.utc)
    closest_state_data = min(iss_data[data_off:], key=lambda x: abs(datetime.strptime(x['state']['timestamp'], '%Y-%jT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc) - now))
    state = closest_state_data['state']
    velocity = state['velocity']
    instantaneous_speed = (velocity['x_dot'] ** 2 + velocity['y_dot'] ** 2 + velocity['z_dot'] ** 2) ** 0.5
    output = "Closest Epoch (UTC):\n"
    output += f"Timestamp: {state['timestamp']}\n"
    #output += print_position_velocity_data(state, indent='   ')
    output += f"Instantaneous Speed (km/s): {instantaneous_speed}\n"
    position = state['position']
    x = float(position['x'])
    y = float(position['y'])
    z = float(position['z'])
    hrs = int(state['timestamp'][9:11])
    mins = int(state['timestamp'][12:14])
    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2))) 
    alt = math.sqrt(x**2 + y**2 + z**2) - 6371
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 5
    if lon > 180: lon = -180 + (lon - 180)
    if lon < -180: lon = 180 + (lon + 180)    
    geocoder = Nominatim(user_agent='iss_tracker')
    location = geocoder.reverse((lat, lon), zoom=15, language='en')
    if location is not None:
        address = location.raw['address']
    else:
        #logger.warning['warning: No location data found. Check if over ocean.']
        address = 'No location data obtained, likely over ocean.'
    output += 'Altitude (km) = '+ str(alt)+'\nLatitude = ' + str(lat) + '\nLongitude = ' + str(lon) + '\nGeolocation = ' + str(address) + '\n'
    return output

@app.route('/comment', methods=['GET'])
def get_comments() -> str:
    """
    Route to return comments from ISS data.

    Returns:
        str: String containing comments.
    """
    if iss_data:
        comments = iss_data[0].get('comments', [])
        #output = "Comments:\n"
        #for comment in comments:
        #    output += f"{comment}\n"
        return comments
    else:
        logger.error['error: could not find ISS data']
        return "No ISS data available."
    
@app.route('/header', methods=['GET'])
def get_header() -> str:
    """
    Route to return header from ISS data.

    Returns:
        str: String containing header elements.
    """
    if iss_data:
        header = iss_data[1]
    if header:
        #header_info = header['header'][0]
        #output = "Header:\n"
        #output += f"Creation Date: {header_info.get('CREATION_DATE', 'N/A')}\n"
        #output += f"Originator: {header_info.get('ORIGINATOR', 'N/A')}\n"
        return header
    else:
        logger.error['error: could not find ISS data']
        return "No header data available."
    
@app.route('/metadata', methods=['GET'])
def get_metadata() -> str:
    """
    Route to return comments from ISS data.

    Returns:
        str: String containing metadata elements.
    """
    if iss_data:
        metadata = iss_data[2]
    if metadata:
        #metadata_info = metadata['metadata'][0]
        #output = "Metadata:\n"
        #output += f"Object Name: {metadata_info.get('OBJECT_NAME', 'N/A')}\n"
        #output += f"Object ID: {metadata_info.get('OBJECT_ID', 'N/A')}\n"   
        #output += f"Center Name: {metadata_info.get('CENTER_NAME', 'N/A')}\n"
        #output += f"Reference Frame: {metadata_info.get('REF_FRAME', 'N/A')}\n"
        #output += f"Time System: {metadata_info.get('TIME_SYSTEM', 'N/A')}\n"
        #output += f"Start Time: {metadata_info.get('START_TIME', 'N/A')}\n"
        #output += f"Stop Time: {metadata_info.get('STOP_TIME', 'N/A')}\n"
        return metadata
    else:
        logger.error['error: could not find ISS data']  
        return "No metadata available."
    
@app.route('/epochs/<epoch>/location', methods=['GET'])
def get_location(epoch: str) -> str:
    """
    Route to return latitude, longitude, altitude, and geoposition for a specific Epoch

    Returns:
        str: String containing altitude, geoposition, latitude, and longitude.
    """
    state_data = next((data for data in iss_data[data_off:] if data['state']['timestamp'] == epoch), None)
    if state_data:
        state = state_data['state']
        position = state['position']
        x = float(position['x'])
        y = float(position['y'])
        z = float(position['z'])
        hrs = int(state['timestamp'][9:11])
        mins = int(state['timestamp'][12:14])
        lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2))) 
        alt = math.sqrt(x**2 + y**2 + z**2) - 6371
        lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 5
        if lon > 180: lon = -180 + (lon - 180)
        if lon < -180: lon = 180 + (lon + 180)    
        geocoder = Nominatim(user_agent='iss_tracker')
        location = geocoder.reverse((lat, lon), zoom=15, language='en')
        if location is not None:
            address = location.raw['address']
        else:
            #logger.warning['warning: No location data found. Check if over ocean.']
            address = 'No location data obtained, likely over ocean.'

        output = {
                "latitude": lat,
                "longitude": lon,
                "geolocation": address,
                "altitude": alt
            }
        return output

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')