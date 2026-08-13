import pytest
import httpx
import secrets
import os


API_URL = os.getenv("DATALOGGER_API_URL", "http://127.0.0.1:8000/api")
MAX_INT = 2_147_483_647

@pytest.fixture
def register_device() -> int:
    """ Register a device with a random ID and return it. """
    device_id = secrets.randbelow(MAX_INT)

    with httpx.Client(base_url=API_URL, timeout=2.0) as client:
        response = client.post(f"/device/register/{device_id}")

    # if ID already exists
    if response.status_code == 409:
        return register_device()

    assert response.status_code == 201, response.text
    return device_id