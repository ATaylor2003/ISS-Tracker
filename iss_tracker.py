import requests
import xmltodict
from datetime import datetime
import logging
from typing import List, Dict, Any
from flask import Flask, request

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

        # Initialize the ISS data list
        iss_data = []

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
            iss_data.append({'timestamp': epoch, 'position': position, 'velocity': velocity})

        return iss_data
    except Exception as e:
        logger.error(f"Error fetching or parsing ISS data: {e}")
        return []

# Get the ISS data
iss_data = fetch_iss_data()

# Function to print position and velocity data with proper formatting
def print_position_velocity_data(position: Dict[str, Any], velocity: Dict[str, Any], indent: str = '') -> str:
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
    output += f"{indent}Position:\n"
    for axis, value in position.items():
        output += f"{indent}   {axis} = {value}\n"
    output += f"{indent}Velocity:\n"
    for axis, value in velocity.items():
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
    limit = int(request.args.get('limit', len(iss_data)-offset))
    modified_epochs = iss_data[offset:offset+limit]
    output = "Epochs:\n"
    for epoch in modified_epochs:
        output += f"Timestamp: {epoch['timestamp']}\n"
        output += print_position_velocity_data(epoch['position'], epoch['velocity'], indent='   ')
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
    state_vector = next((epoch_data for epoch_data in iss_data if epoch_data['timestamp'] == epoch), None)
    if state_vector:
        output = "State Vector:\n"
        output += f"Timestamp: {state_vector['timestamp']}\n"
        output += print_position_velocity_data(state_vector['position'], state_vector['velocity'], indent='   ')
        return output
    else:
        logger.error({'error': 'State vector not found for the given epoch'})
        return str("")

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
    state_vector = next((epoch_data for epoch_data in iss_data if epoch_data['timestamp'] == epoch), None)
    if state_vector:
        instantaneous_speed = (state_vector['velocity']['x_dot'] ** 2 + state_vector['velocity']['y_dot'] ** 2 + state_vector['velocity']['z_dot'] ** 2) ** 0.5
        output = f"Instantaneous Speed: {instantaneous_speed}\n"
        return output
    else:
        logger.error({'error': 'State vector not found for the given epoch'})
        return str("")

# Route to return state vectors and instantaneous speed for the epoch nearest in time
@app.route('/now', methods=['GET'])
def get_nearest_epoch() -> str:
    """
    Route to return state vectors and instantaneous speed for the epoch nearest in time.

    Returns:
        str: String containing formatted epoch and speed data.
    """
    now = datetime.now()
    closest_epoch = min(iss_data, key=lambda x: abs(datetime.strptime(x['timestamp'], '%Y-%jT%H:%M:%S.%fZ') - now))
    instantaneous_speed = (closest_epoch['velocity']['x_dot'] ** 2 + closest_epoch['velocity']['y_dot'] ** 2 + closest_epoch['velocity']['z_dot'] ** 2) ** 0.5
    output = "Closest Epoch:\n"
    output += f"Timestamp: {closest_epoch['timestamp']}\n"
    output += print_position_velocity_data(closest_epoch['position'], closest_epoch['velocity'], indent='   ')
    output += f"Instantaneous Speed: {instantaneous_speed}\n"
    return output

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')