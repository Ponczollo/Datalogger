import os
import secrets
from datetime import datetime, timezone
import httpx
import pytest


API_URL = os.getenv("DATALOGGER_API_URL", "http://127.0.0.1:8000/api")
MAX_INT = 2_147_483_647


@pytest.fixture
def register_device() -> int:
    """
    Register a device with a random ID
    Returns DEVICE ID
    """

    device_id = secrets.randbelow(MAX_INT)

    with httpx.Client(base_url=API_URL, timeout=2.0) as client:
        response = client.post(f"/device/register/{device_id}")

    # if ID already exists
    if response.status_code == 409:
        return register_device()

    assert response.status_code == 201, response.text
    return device_id


@pytest.fixture
def register_user() -> int:
    """
    Register a user with a random ID
    Returns USER ID
    """
    user_id = secrets.randbelow(MAX_INT)
    
    with httpx.Client(base_url=API_URL, timeout=2.0) as client:
        response = client.post(f"/user/register/{user_id}")
    
    # if ID already exists
    if response.status_code == 409:
        return register_device()
    
    assert response.status_code == 201, response.text
    return user_id


@pytest.fixture
def user_device_pair(register_user: int, register_device: int) -> tuple[int, int]:
    """ 
    Register user and device and connect them
    Returns (USER ID, DEVICE ID) pair
    """
    with httpx.Client(base_url=API_URL, timeout=2.0) as client:
        response = client.post(f"/user/add_device/{register_user}/{register_device}")

    assert response.status_code == 201, response.text
    return register_user, register_device