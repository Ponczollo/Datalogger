from numbers import Real

from smbus import SMBus

from rpi.gyroacc import MPU9250, Vector3, MotionData


def test_reads_accelerometer_and_gyroscope_from_mpu9250():
    bus = SMBus(1)
    try:
        motion_data = MPU9250(bus).read()
        acceleration = motion_data.acceleration
        gyroscope = motion_data.gyroscope
    finally:
        bus.close()

    assert isinstance(acceleration, Vector3)
    assert isinstance(gyroscope, Vector3)
    assert all(isinstance(value, Real) for value in MotionData(acceleration, gyroscope).to_dict().values())
