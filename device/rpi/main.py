import json
import logging
import os
import queue
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from smbus2 import SMBus

from rpi.gyroacc import MPU9250
from rpi.temphum import AHT10, AHT10Error


MOTION_INTERVAL = 0.01
TEMPHUM_INTERVAL = 1.0
UPLOAD_INTERVAL = 1.0
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

logger = logging.getLogger(__name__)



def unix_milliseconds() -> int:
    return time.time_ns() // 1_000_000


def read_motion(mpu: MPU9250) -> dict[str, int]:
    data = mpu.read()
    return {
        "acc_x": round(data.acceleration.x * 1000),
        "acc_y": round(data.acceleration.y * 1000),
        "acc_z": round(data.acceleration.z * 1000),
        "gyro_x": round(data.gyroscope.x),
        "gyro_y": round(data.gyroscope.y),
        "gyro_z": round(data.gyroscope.z),
    }


def read_temphum(aht: AHT10) -> dict[str, int]:
    data = aht.read()
    return {
        "temperature": round(data.temperature),
        "humidity": round(data.humidity),
    }


def temphum_worker(
    readings: queue.Queue,
    stop: threading.Event,
    bus_number: int,
) -> None:
    with SMBus(bus_number) as bus:
        aht = AHT10(bus)
        next_read = time.monotonic()

        while not stop.is_set():
            try:
                values = read_temphum(aht)
                readings.put((unix_milliseconds(), values))
            except (AHT10Error, OSError) as error:
                logger.warning("AHT10 read failed: %s", error)

            next_read += TEMPHUM_INTERVAL
            stop.wait(max(0.0, next_read - time.monotonic()))


def post_readings(url: str, readings: dict[int, dict[str, int]]) -> None:
    body = json.dumps(readings).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=5) as response:
        if response.status != 201:
            raise RuntimeError(f"Backend returned HTTP {response.status}")


def upload_worker(
    readings: queue.Queue,
    stop: threading.Event,
    url: str,
) -> None:
    batch: dict[int, dict[str, int]] = {}
    next_upload = time.monotonic() + UPLOAD_INTERVAL

    while not stop.is_set() or not readings.empty():
        timeout = max(0.0, next_upload - time.monotonic())
        try:
            timestamp, values = readings.get(timeout=timeout)
            batch.setdefault(timestamp, {}).update(values)
        except queue.Empty:
            pass

        if time.monotonic() < next_upload and not stop.is_set():
            continue

        if batch:
            try:
                post_readings(url, batch)
                batch.clear()
            except HTTPError as error:
                detail = error.read().decode("utf-8", errors="replace")
                logger.warning(
                    "Upload failed with HTTP %s: %s; keeping batch for retry",
                    error.code,
                    detail,
                )
            except (URLError, TimeoutError, RuntimeError) as error:
                logger.warning("Upload failed; keeping batch for retry: %s", error)

        next_upload = time.monotonic() + UPLOAD_INTERVAL


def register_device(api_url: str, device_id: int) -> None:
    url = f"{api_url}/device/register/{device_id}"
    request = Request(url, data=b"", method="POST")

    try:
        with urlopen(request, timeout=5) as response:
            if response.status != 201:
                raise RuntimeError(f"Backend returned HTTP {response.status}")
            logger.info("Registered device %s", device_id)
    except HTTPError as error:
        if error.code == 409:
            logger.info("Device %s is already registered", device_id)
            return

        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Device registration failed with HTTP {error.code}: {detail}"
        ) from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"Could not connect to backend: {error}") from error


def main() -> None:
    if not load_dotenv(ENV_PATH):
        raise RuntimeError(f"Environment file not found or empty: {ENV_PATH}")

    api_url = os.environ.get("API_URL", "http://127.0.0.1:8000/api").rstrip("/")
    try:
        device_id = int(os.environ["DEVICE_ID"])
        bus_number = int(os.environ.get("I2C_BUS", "1"))
    except KeyError as error:
        raise RuntimeError("DEVICE_ID must be set in the project .env file") from error
    except ValueError as error:
        raise RuntimeError("DEVICE_ID and I2C_BUS must be integers") from error

    register_device(api_url, device_id)

    upload_url = f"{api_url}/device/log/{device_id}"
    readings: queue.Queue = queue.Queue()
    stop = threading.Event()

    workers = [
        threading.Thread(
            target=temphum_worker,
            args=(readings, stop, bus_number),
            name="temphum",
        ),
        threading.Thread(
            target=upload_worker,
            args=(readings, stop, upload_url),
            name="uploader",
        ),
    ]

    for worker in workers:
        worker.start()

    try:
        with SMBus(bus_number) as bus:
            mpu = MPU9250(bus)
            next_read = time.monotonic()

            while True:
                values = read_motion(mpu)
                readings.put((unix_milliseconds(), values))
                next_read += MOTION_INTERVAL
                delay = next_read - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_read = time.monotonic()
    except KeyboardInterrupt:
        logger.info("Stopping data logger")
    finally:
        stop.set()
        for worker in workers:
            worker.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
