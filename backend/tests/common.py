import os
import secrets
from datetime import datetime, timezone

API_URL = os.getenv("DATALOGGER_API_URL", "http://127.0.0.1:8000/api")
MAX_INT = 2_147_483_647


def create_log_data() -> dict[str, dict[str, int | str]]:
    timestamp = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    return {
        str(timestamp): {
            "temperature": secrets.randbelow(100),
            "humidity": secrets.randbelow(100),
            "gps": "$GPGGA,000000.00,0000.000,N,00000.000,E,1,00,1.0,0.0,M,0.0,M,,",
            "gyro_x": secrets.randbelow(1000),
            "gyro_y": secrets.randbelow(1000),
            "gyro_z": secrets.randbelow(1000),
            "acc_x": secrets.randbelow(1000),
            "acc_y": secrets.randbelow(1000),
            "acc_z": secrets.randbelow(1000),
        }
    }