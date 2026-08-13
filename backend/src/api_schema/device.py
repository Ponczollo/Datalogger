from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

Timestamp = Annotated[int, Field(ge=0)]

class SensorReading(BaseModel):

    model_config = ConfigDict(extra="forbid")

    gps: str | None = Field(default=None, max_length=255)
    gyro_x: int | None = None
    gyro_y: int | None = None
    gyro_z: int | None = None
    acc_x: int | None = None
    acc_y: int | None = None
    acc_z: int | None = None
    temperature: int | None = None
    humidity: int | None = None

    @model_validator(mode="after")
    def has_measurement(self) -> "SensorReading":
        if not any(value is not None for value in self.model_dump().values()):
            raise ValueError("No measurements in timestamp")
        return self


class DeviceLogRequest(RootModel[dict[Timestamp, SensorReading]]):
    """ Batch of sensor readings, keys are Unix milisecond timestamps """
