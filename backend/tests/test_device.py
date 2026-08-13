from datetime import datetime, timezone
import os
import secrets
import httpx
import pytest

from common import register_device, API_URL, MAX_INT


def test_upload_device_readings(register_device: int) -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    start_milliseconds = int(start.timestamp() * 1000)
    timestamps = {
        "one_millisecond": start_milliseconds + 1,
        "one_second": start_milliseconds + 1_000,
        "one_hour": start_milliseconds + 3_600_000,
        "one_day": start_milliseconds + 86_400_000,
    }
    payload = {
        str(timestamps["one_millisecond"]): {"acc_x": 1, "acc_y": 2, "acc_z": 3},
        str(timestamps["one_second"]): {"gyro_x": 4, "gyro_y": 5, "gyro_z": 6},
        str(timestamps["one_hour"]): {"temperature": 22, "humidity": 55},
        str(timestamps["one_day"]): {"gps": "$GPGGA,000000.00,0000.000,N,00000.000,E,1,00,1.0,0.0,M,0.0,M,,"},
    }

    with httpx.Client(base_url=API_URL, timeout=5.0) as client:
        response = client.post(f"/device/log/{register_device}", json=payload)

    assert response.status_code == 201, response.text
    assert response.json() == {"status": "OK"}
