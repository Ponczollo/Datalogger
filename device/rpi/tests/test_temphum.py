from numbers import Real

from smbus2 import SMBus

from rpi.temphum import AHT10, TemperatureHumidityData


def test_reads_temperature_and_humidity_from_aht10():
    bus = SMBus(1)
    try:
        data = AHT10(bus).read()
    finally:
        bus.close()

    assert isinstance(data, TemperatureHumidityData)
    assert isinstance(data.temperature, Real)
    assert isinstance(data.humidity, Real)
    assert -50.0 <= data.temperature <= 150.0
    assert 0.0 <= data.humidity <= 100.0
