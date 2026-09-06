import time

from smbus2 import SMBus

from rpi.temphum import AHT10

bus = SMBus(1)
try:
    aht = AHT10(bus)
    while True:
        data = aht.read()
        temperature = data.temperature
        humidity = data.humidity
        print(f"{temperature:5.1f} °C  {humidity:5.1f} %RH")
        time.sleep(1)

finally:
    bus.close()
