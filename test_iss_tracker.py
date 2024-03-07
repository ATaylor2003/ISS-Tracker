import pytest
from datetime import datetime
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

def test_print_position_velocity_data():
    position = {'x': 10.0, 'y': 20.0, 'z': 30.0}
    velocity = {'x_dot': 1.0, 'y_dot': 2.0, 'z_dot': 3.0}
    output = print_position_velocity_data(position, velocity)
    expected_output = (
        "Position:\n"
        "   x = 10.0\n"
        "   y = 20.0\n"
        "   z = 30.0\n"
        "Velocity:\n"
        "   x_dot = 1.0\n"
        "   y_dot = 2.0\n"
        "   z_dot = 3.0\n"
    )
    assert output == expected_output

def test_get_epochs(client):
    response = client.get('/epochs')
    assert response.status_code == 200

def test_get_state_vectors(client):
    response = client.get('/epochs/2024-055T18:29:57.887687Z')
    assert response.status_code == 200

def test_get_instantaneous_speed(client):
    response = client.get('/epochs/2024-055T18:29:57.887687Z/speed')
    assert response.status_code == 200

def test_get_nearest_epoch(client):
    response = client.get('/now')
    assert response.status_code == 200