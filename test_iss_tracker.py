import pytest
from datetime import datetime
import pytz
from iss_tracker import app, fetch_iss_data, print_position_velocity_data

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_fetch_iss_data():
    iss_data = fetch_iss_data()
    assert isinstance(iss_data, list)
    assert len(iss_data) > 0
    assert all(isinstance(entry, dict) for entry in iss_data)

def test_get_epochs(client):
    response = client.get('/epochs')
    assert response.status_code == 200

def test_get_state_vectors(client):
    response = client.get('/epochs/2024-055T18:32:00.000Z')
    assert response.status_code == 200

def test_get_instantaneous_speed(client):
    response = client.get('/epochs/2024-055T18:32:00.000Z/speed')
    assert response.status_code == 200

def test_print_position_velocity_data():
    # Define a sample state dictionary
    state = {
        'position': {'x': 10, 'y': 20, 'z': 30},
        'velocity': {'vx': 5, 'vy': -2, 'vz': 8}
    }

    # Call the function with the sample state dictionary
    output = print_position_velocity_data(state)

    # Define the expected output string
    expected_output = (
        "Position:\n"
        "   x = 10\n"
        "   y = 20\n"
        "   z = 30\n"
        "Velocity:\n"
        "   vx = 5\n"
        "   vy = -2\n"
        "   vz = 8\n"
    )

    # Assert that the output matches the expected output
    assert output == expected_output

def test_get_location(client):
    now = datetime.now(pytz.utc)
    dt_i = datetime.strftime(now, '%Y-%jT%H:%M:%S.%fZ')
    form_date = datetime.strptime(dt_i,'%Y-%jT%H:%M:%S.%fZ')
    min = ((form_date.minute+3)//4)*4
    dt_p = form_date.replace(minute=min, second=0, microsecond=0)
    dt = datetime.strftime(dt_p, '%Y-%jT%H:%M:%S.%fZ')[:-4]+'Z'
    input = '/epochs/'+dt+'/location'
    response = client.get(input)
    assert response.status_code == 200

def test_get_nearest_epoch(client):
    response = client.get('/now')
    assert response.status_code == 200

def test_get_comment(client):
    response = client.get('/comment')
    assert response.status_code == 200

def test_get_header(client):
    response = client.get('/header')
    assert response.status_code == 200

def test_get_metadata(client):
    response = client.get('/metadata')
    assert response.status_code == 200