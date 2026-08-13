import httpx

from common import API_URL, create_log_data


def test_fetch_uploaded_device_readings(user_device_pair: tuple[int, int]) -> None:
    user_id, device_id = user_device_pair
    payload = create_log_data()
    timestamp = next(iter(payload))

    with httpx.Client(base_url=API_URL, timeout=5.0) as client:
        upload_response = client.post(f"/device/log/{device_id}", json=payload)
        fetch_response = client.get(f"/user/data/all/{user_id}")

    assert upload_response.status_code == 201, upload_response.text
    assert fetch_response.status_code == 200, fetch_response.text

    device_data = fetch_response.json()["devices"]

    assert len(device_data) == 1
    assert device_data[0]["id"] == device_id

    assert device_data[0]["gps"] == [{
        "time": int(timestamp),
        "sentence": payload[timestamp]["gps"],
    }]

    assert device_data[0]["gyroacc"] == [{
        "time": int(timestamp),
        "gyro_x": payload[timestamp]["gyro_x"],
        "gyro_y": payload[timestamp]["gyro_y"],
        "gyro_z": payload[timestamp]["gyro_z"],
        "acc_x": payload[timestamp]["acc_x"],
        "acc_y": payload[timestamp]["acc_y"],
        "acc_z": payload[timestamp]["acc_z"],
    }]

    assert device_data[0]["temphum"] == [{
        "time": int(timestamp),
        "temperature": payload[timestamp]["temperature"],
        "humidity": payload[timestamp]["humidity"],
    }]
