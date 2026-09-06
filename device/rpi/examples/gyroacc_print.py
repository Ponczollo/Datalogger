import time

from smbus2 import SMBus

from rpi.gyroacc import MPU9250

bus = SMBus(1)
try:
    mpu = MPU9250(bus)
    while True:
        data = mpu.read()
        acceleration = data.acceleration
        gyroscope = data.gyroscope
        print(f"{acceleration.x:5.1f} {acceleration.y:5.1f} {acceleration.z:5.1f} {gyroscope.x:5.1f} {gyroscope.y:5.1f} {gyroscope.z:5.1f}")
        time.sleep(0.1)

finally:
    bus.close()
