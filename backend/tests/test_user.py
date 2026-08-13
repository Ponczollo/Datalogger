from datetime import datetime, timezone
import secrets

import httpx

from common import API_URL, MAX_INT, register_device


def test_fetch_uploaded_device_readings(register_device: int) -> None:
    user_id = secrets.randbelow(MAX_INT - 1) + 1
    timestamp = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    gps_sentence = "$GPGGA,000000.00,0000.000,N,00000.000,E,1,00,1.0,0.0,M,0.0,M,,"
    payload = {
        str(timestamp): {
            "temperature": 22,
            "humidity": 55,
            "gps": gps_sentence,
            "gyro_x": 1,
            "gyro_y": 2,
            "gyro_z": 3,
            "acc_x": 4,
            "acc_y": 5,
            "acc_z": 6,
        }
    }

    with httpx.Client(base_url=API_URL, timeout=5.0) as client:
        register_user_response = client.post(f"/user/register/{user_id}")
        connect_device_response = client.post(f"/user/add_device/{user_id}/{register_device}")
        upload_response = client.post(f"/device/log/{register_device}", json=payload)
        fetch_response = client.get(f"/user/data/all/{user_id}")

    assert register_user_response.status_code == 201, register_user_response.text
    assert connect_device_response.status_code == 201, connect_device_response.text
    assert upload_response.status_code == 201, upload_response.text
    assert fetch_response.status_code == 200, fetch_response.text

    device_data = fetch_response.json()["devices"]
    assert len(device_data) == 1
    assert device_data[0]["id"] == register_device
    assert device_data[0]["gps"] == [{"time": timestamp, "sentence": gps_sentence}]
    assert device_data[0]["gyroacc"] == [{
        "time": timestamp,
        "gyro_x": 1,
        "gyro_y": 2,
        "gyro_z": 3,
        "acc_x": 4,
        "acc_y": 5,
        "acc_z": 6,
    }]
    assert device_data[0]["temphum"] == [{
        "time": timestamp,
        "temperature": 22,
        "humidity": 55,
    }]
