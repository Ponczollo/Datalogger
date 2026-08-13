from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.database.models import Device, User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_with_device_data(self, user_id: int) -> User | None:
        statement = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.devices).selectinload(Device.gps_readings),
                selectinload(User.devices).selectinload(Device.gyroacc_readings),
                selectinload(User.devices).selectinload(Device.temphum_readings),
            )
        )
        return self.db.scalar(statement)

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def add_user(self, user_id: int) -> User:
        user = User(id=user_id, name=f"USER_{user_id}")
        self.db.add(user)
        return user

    def get_device(self, device_id: int) -> Device | None:
        return self.db.get(Device, device_id)

    def add_device(self, user: User, device: Device) -> None:
        user.devices.append(device)
