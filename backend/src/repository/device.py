from sqlalchemy.orm import Session

from src.api_schema.device import DeviceLogRequest, SensorReading
from src.database.models.device import Device
from src.database.models.gps import GPS
from src.database.models.gyroacc import GyroAcc
from src.database.models.temphum import TempHum


class DeviceRepository:

    def __init__(self, db: Session):
        self.db = db

    def exists(self, device_id: int) -> bool:
        return self.db.get(Device, device_id) is not None

    def add_device(self, device_id: int) -> Device:
        device = Device(id=device_id, name=f"DEVICE_{device_id}")
        self.db.add(device)
        return device

    def add_log_entries(self, device_id: int, payload: DeviceLogRequest) -> None:
        for timestamp, reading in payload.root.items():
            self._add_reading(device_id, timestamp, reading)

    def _add_reading(self, device_id: int, timestamp: int, reading: SensorReading) -> None:
        if reading.gps is not None:
            self.db.add(GPS(device_id=device_id, time=timestamp, sentence=reading.gps))

        gyroacc_fields = ("gyro_x", "gyro_y", "gyro_z", "acc_x", "acc_y", "acc_z")
        if any(getattr(reading, field) is not None for field in gyroacc_fields):
            self.db.add(GyroAcc(device_id=device_id, time=timestamp, **{field: getattr(reading, field) for field in gyroacc_fields}))

        if reading.temperature is not None or reading.humidity is not None:
            self.db.add(TempHum(device_id=device_id, time=timestamp, temperature=reading.temperature, humidity=reading.humidity))
