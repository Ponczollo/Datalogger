from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api_schema.device import DeviceLogRequest
from src.dependencies import get_db
from src.processor.device import DeviceAlreadyRegisteredError, DeviceNotFoundError, DeviceProcessor


class DeviceController:

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/device", tags=["device"])
        self.router.add_api_route("/log/{device_id}", self.log_device_data, methods=["POST"], status_code=status.HTTP_201_CREATED)
        self.router.add_api_route("/register/{device_id}", self.register_device, methods=["POST"], status_code=status.HTTP_201_CREATED)

    def register_device(self, device_id: int, db: Session = Depends(get_db)) -> dict[str, int | str]:
        try:
            name = DeviceProcessor(db).register(device_id)
        except DeviceAlreadyRegisteredError as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device is already registered") from error
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown error")

        return {"id": device_id, "name": name}

    def log_device_data(self, device_id: int, payload: DeviceLogRequest, db: Session = Depends(get_db)) -> dict[str, str]:
        try:
            DeviceProcessor(db).process_log(device_id, payload)
            db.commit()
        except DeviceNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device is not registered") from error
        except Exception:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown error")

        return {"status": "OK"}


device_controller = DeviceController()
device_router = device_controller.router
