import time
from dataclasses import dataclass

from smbus2 import SMBus, i2c_msg


@dataclass(frozen=True)
class TemperatureHumidityData:
    temperature: float
    humidity: float

    def to_dict(self):
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
        }


class AHT10Error(RuntimeError):
    pass


class AHT10:
    BASE_ADDRESS = 0x38

    _INITIALIZE = 0xE1
    _TRIGGER_MEASUREMENT = 0xAC
    _CALIBRATED = 0x08
    _BUSY = 0x80
    _MEASUREMENT_DELAY = 0.2

    def __init__(self, bus: SMBus, address=BASE_ADDRESS):
        self.bus = bus
        self.address = address
        self._initialize()

    def _initialize(self):
        time.sleep(0.02)
        if not self._read_bytes(1)[0] & self._CALIBRATED:
            self._write_bytes(self._INITIALIZE, 0x08, 0x00)
            time.sleep(0.01)

    def _write_bytes(self, *data):
        message = i2c_msg.write(self.address, data)
        self.bus.i2c_rdwr(message)

    def _read_bytes(self, length):
        message = i2c_msg.read(self.address, length)
        self.bus.i2c_rdwr(message)
        return list(message)

    def read(self):
        self._write_bytes(self._TRIGGER_MEASUREMENT, 0x33, 0x00)
        time.sleep(self._MEASUREMENT_DELAY)

        data = self._read_bytes(6)
        if len(data) != 6:
            raise AHT10Error(f"Expected 6 data bytes, received {len(data)}")
        if data[0] & self._BUSY:
            raise AHT10Error("Measurement timed out while sensor was busy")

        humidity_raw = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
        temperature_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

        return TemperatureHumidityData(
            temperature=temperature_raw * 200.0 / (1 << 20) - 50.0,
            humidity=humidity_raw * 100.0 / (1 << 20),
        )

    def read_temperature(self):
        return self.read().temperature

    def read_humidity(self):
        return self.read().humidity
