from pydantic import BaseModel


class GPSReadingResponse(BaseModel):
    time: int | None
    sentence: str


class GyroAccReadingResponse(BaseModel):
    time: int | None
    gyro_x: int | None
    gyro_y: int | None
    gyro_z: int | None
    acc_x: int | None
    acc_y: int | None
    acc_z: int | None


class TempHumReadingResponse(BaseModel):
    time: int | None
    temperature: int | None
    humidity: int | None


class DeviceDataResponse(BaseModel):
    id: int
    name: str
    gps: list[GPSReadingResponse]
    gyroacc: list[GyroAccReadingResponse]
    temphum: list[TempHumReadingResponse]


class UserDataResponse(BaseModel):
    id: int
    name: str
    devices: list[DeviceDataResponse]
