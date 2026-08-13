import httpx

from common import API_URL, create_log_data

def test_upload_device_readings(register_device: int) -> None:
    log_data = create_log_data()

    with httpx.Client(base_url=API_URL, timeout=5.0) as client:
        response = client.post(f"/device/log/{register_device}", json=log_data)

    assert response.status_code == 201, response.text
    assert response.json() == {"status": "OK"}
