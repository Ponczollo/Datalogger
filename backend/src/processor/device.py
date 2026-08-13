from sqlalchemy.orm import Session

from src.api_schema.device import DeviceLogRequest
from src.repository.device import DeviceRepository


class DeviceNotFoundError(Exception):
    pass


class DeviceAlreadyRegisteredError(Exception):
    pass


class DeviceProcessor:

    def __init__(self, db: Session):
        self.repository = DeviceRepository(db)

    def process_log(self, device_id: int, payload: DeviceLogRequest) -> None:
        if not self.repository.exists(device_id):
            raise DeviceNotFoundError

        return self.repository.add_log_entries(device_id, payload)

    def register(self, device_id: int) -> str:
        if self.repository.exists(device_id):
            raise DeviceAlreadyRegisteredError

        return self.repository.add_device(device_id).name
