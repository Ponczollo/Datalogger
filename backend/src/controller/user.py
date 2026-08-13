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
        self.router.add_api_route(
            "/data/all/{user_id}",
            self.get_user_data,
            methods=["GET"],
            response_model=UserDataResponse,
        )
        self.router.add_api_route(
            "/data/single/{user_id}/{timestamp}",
            self.get_single_user_data,
            methods=["GET"],
            response_model=UserDataResponse,
        )
        self.router.add_api_route(
            "/data/since/{user_id}/{timestamp}",
            self.get_user_data_since,
            methods=["GET"],
            response_model=UserDataResponse,
        )
        self.router.add_api_route(
            "/data/until/{user_id}/{timestamp}",
            self.get_user_data_until,
            methods=["GET"],
            response_model=UserDataResponse,
        )
        self.router.add_api_route(
            "/data/range/{user_id}/{start}/{end}",
            self.get_user_data_range,
            methods=["GET"],
            response_model=UserDataResponse,
        )


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


    def get_user_data(self, user_id: int, db: Session = Depends(get_db)) -> UserDataResponse:
        return self._get_user_data(user_id, db)

    def get_single_user_data(
        self,
        user_id: int,
        timestamp: int,
        db: Session = Depends(get_db),
    ) -> UserDataResponse:
        return self._get_user_data(user_id, db, start=timestamp, end=timestamp)

    def get_user_data_since(
        self,
        user_id: int,
        timestamp: int,
        db: Session = Depends(get_db),
    ) -> UserDataResponse:
        return self._get_user_data(user_id, db, start=timestamp)

    def get_user_data_until(
        self,
        user_id: int,
        timestamp: int,
        db: Session = Depends(get_db),
    ) -> UserDataResponse:
        return self._get_user_data(user_id, db, end=timestamp)

    def get_user_data_range(
        self,
        user_id: int,
        start: int,
        end: int,
        db: Session = Depends(get_db),
    ) -> UserDataResponse:
        return self._get_user_data(user_id, db, start=start, end=end)

    def _get_user_data(
        self,
        user_id: int,
        db: Session,
        start: int | None = None,
        end: int | None = None,
    ) -> UserDataResponse:
        try:
            return UserProcessor(db).get_data(user_id, start, end)
        except UserNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found") from error

user_controller = UserController()
user_router = user_controller.router
