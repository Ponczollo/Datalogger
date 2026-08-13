from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api_schema.user import UserDataResponse
from src.dependencies import get_db
from src.processor.user import (
    DeviceNotFoundError,
    UserAlreadyRegisteredError,
    UserDeviceAlreadyConnectedError,
    UserNotFoundError,
    UserProcessor,
)


class UserController:

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/user", tags=["user"])
        self.router.add_api_route(
            "/data/all/{user_id}",
            self.get_user_data,
            methods=["GET"],
            response_model=UserDataResponse,
        )
        self.router.add_api_route(
            "/register/{user_id}",
            self.register_user,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            "/add_device/{user_id}/{device_id}",
            self.add_device,
            methods=["POST"],
            status_code=status.HTTP_201_CREATED,
        )

    def get_user_data(self, user_id: int, db: Session = Depends(get_db)) -> UserDataResponse:
        try:
            return UserProcessor(db).get_data(user_id)
        except UserNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found") from error

    def register_user(self, user_id: int, db: Session = Depends(get_db)) -> dict[str, int | str]:
        try:
            name = UserProcessor(db).register(user_id)
            db.commit()
        except UserAlreadyRegisteredError as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already registered") from error
        except Exception as error:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown error") from error

        return {"id": user_id, "name": name}

    def add_device(
        self,
        user_id: int,
        device_id: int,
        db: Session = Depends(get_db),
    ) -> dict[str, int | str]:
        try:
            UserProcessor(db).add_device(user_id, device_id)
            db.commit()
        except UserNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found") from error
        except DeviceNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device was not found") from error
        except UserDeviceAlreadyConnectedError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Device is already connected to the user",
            ) from error
        except Exception as error:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown error") from error

        return {"status": "OK", "user_id": user_id, "device_id": device_id}


user_controller = UserController()
user_router = user_controller.router
