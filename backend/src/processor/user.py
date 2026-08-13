from sqlalchemy.orm import Session

from src.api_schema.user import (
    DeviceDataResponse,
    GPSReadingResponse,
    GyroAccReadingResponse,
    TempHumReadingResponse,
    UserDataResponse,
)
from src.repository.user import UserRepository


class UserNotFoundError(Exception):
    pass


class UserAlreadyRegisteredError(Exception):
    pass


class UserDeviceAlreadyConnectedError(Exception):
    pass


class DeviceNotFoundError(Exception):
    pass


class UserProcessor:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_data(
        self,
        user_id: int,
        start: int | None = None,
        end: int | None = None,
    ) -> UserDataResponse:
        user = self.repository.get_with_device_data(user_id, start, end)
        if user is None:
            raise UserNotFoundError

        return UserDataResponse(
            id=user.id,
            name=user.name,
            devices=[
                DeviceDataResponse(
                    id=device.id,
                    name=device.name,
                    gps=[
                        GPSReadingResponse(time=reading.time, sentence=reading.sentence)
                        for reading in sorted(device.gps_readings, key=lambda reading: reading.time or 0)
                    ],
                    gyroacc=[
                        GyroAccReadingResponse(
                            time=reading.time,
                            gyro_x=reading.gyro_x,
                            gyro_y=reading.gyro_y,
                            gyro_z=reading.gyro_z,
                            acc_x=reading.acc_x,
                            acc_y=reading.acc_y,
                            acc_z=reading.acc_z,
                        )
                        for reading in sorted(device.gyroacc_readings, key=lambda reading: reading.time or 0)
                    ],
                    temphum=[
                        TempHumReadingResponse(
                            time=reading.time,
                            temperature=reading.temperature,
                            humidity=reading.humidity,
                        )
                        for reading in sorted(device.temphum_readings, key=lambda reading: reading.time or 0)
                    ],
                )
                for device in user.devices
            ],
        )

    def register(self, user_id: int) -> str:
        if self.repository.get(user_id) is not None:
            raise UserAlreadyRegisteredError

        return self.repository.add_user(user_id).name

    def add_device(self, user_id: int, device_id: int) -> None:
        user = self.repository.get(user_id)
        if user is None:
            raise UserNotFoundError

        device = self.repository.get_device(device_id)
        if device is None:
            raise DeviceNotFoundError

        if device in user.devices:
            raise UserDeviceAlreadyConnectedError

        self.repository.add_device(user, device)
