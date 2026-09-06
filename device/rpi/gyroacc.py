import time
from dataclasses import dataclass

from smbus2 import SMBus


@dataclass(frozen=True)
class Vector3:
    x: float
    y: float
    z: float

@dataclass(frozen=True)
class MotionData:
    acceleration: Vector3
    gyroscope: Vector3

    def to_dict(self):
        return {
            "acc_x": self.acceleration.x,
            "acc_y": self.acceleration.y,
            "acc_z": self.acceleration.z,
            "gyro_x": self.gyroscope.x,
            "gyro_y": self.gyroscope.y,
            "gyro_z": self.gyroscope.z,
        }


class MPU9250Error(RuntimeError):
    pass


class MPU9250:
    BASE_ADDRESS = 0x68

    _SMPLRT_DIV = 0x19
    _CONFIG = 0x1A
    _GYRO_CONFIG = 0x1B
    _ACCEL_CONFIG = 0x1C
    _ACCEL_CONFIG_2 = 0x1D
    _ACCEL_XOUT_H = 0x3B
    _PWR_MGMT_1 = 0x6B
    _PWR_MGMT_2 = 0x6C
    _WHO_AM_I = 0x75

    _ACCEL_SCALES = {
        2: 16384.0,
        4: 8192.0,
        8: 4096.0,
        16: 2048.0,
    }
    _GYRO_SCALE = 131.0  # LSB/(degrees/s) for the +/- 250 degrees/s range

    def __init__(self, bus: SMBus, address=BASE_ADDRESS):
        self.bus = bus
        self.address = address
        self._accel_scale = self._ACCEL_SCALES[2]
        self._initialize()

    def _initialize(self):
        device_id = self.bus.read_byte_data(self.address, self._WHO_AM_I)
        if device_id not in (0x70, 0x71, 0x73):
            raise MPU9250Error(f"Unexpected WHO_AM_I value 0x{device_id:02X}")

        self.bus.write_byte_data(self.address, self._PWR_MGMT_1, 0x80)
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, self._PWR_MGMT_1, 0x01)
        self.bus.write_byte_data(self.address, self._PWR_MGMT_2, 0x00)
        time.sleep(0.01)

        self.bus.write_byte_data(self.address, self._SMPLRT_DIV, 4)         # 200 Hz sample rate
        self.bus.write_byte_data(self.address, self._CONFIG, 3)             # 41 Hz gyroscope low-pass filter
        self.bus.write_byte_data(self.address, self._GYRO_CONFIG, 0)        # +/- 250 degrees/s
        self.bus.write_byte_data(self.address, self._ACCEL_CONFIG, 0)       # +/- 2 g
        self.bus.write_byte_data(self.address, self._ACCEL_CONFIG_2, 3)     # 41 Hz accelerometer low-pass filter

    def set_accelerometer_range(self, full_scale_g: int):
        """Set range to 2, 4, 8, or 16 g."""
        if full_scale_g not in self._ACCEL_SCALES:
            raise ValueError("Accelerometer range must be one of: 2, 4, 8, 16 g")

        range_bits = {2: 0, 4: 1, 8: 2, 16: 3}[full_scale_g]
        config = self.bus.read_byte_data(self.address, self._ACCEL_CONFIG)
        config = (config & ~0x18) | (range_bits << 3)
        self.bus.write_byte_data(self.address, self._ACCEL_CONFIG, config)
        self._accel_scale = self._ACCEL_SCALES[full_scale_g]

    @staticmethod
    def _signed_16(high, low):
        value = (high << 8) | low
        return value - 0x10000 if value & 0x8000 else value

    def read_raw(self):
        data = self.bus.read_i2c_block_data(self.address, self._ACCEL_XOUT_H, 14)
        if len(data) != 14:
            raise MPU9250Error(f"Expected 14 data bytes, received {len(data)}")

        values = tuple(self._signed_16(data[index], data[index + 1]) for index in (0, 2, 4, 8, 10, 12))
        return values[:3], values[3:]

    def read(self):
        acceleration, gyroscope = self.read_raw()
        return MotionData(
            acceleration=Vector3(*(value / self._accel_scale for value in acceleration)),
            gyroscope=Vector3(*(value / self._GYRO_SCALE for value in gyroscope)),
        )

    def read_accelerometer(self):
        return self.read().acceleration

    def read_gyroscope(self):
        return self.read().gyroscope
