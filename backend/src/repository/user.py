from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.database.models import Device, GPS, GyroAcc, TempHum, User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_with_device_data(
        self,
        user_id: int,
        start: int | None = None,
        end: int | None = None,
    ) -> User | None:
        def readings_loader(relationship, model):
            if start is not None:
                relationship = relationship.and_(model.time >= start)
            if end is not None:
                relationship = relationship.and_(model.time <= end)
            return selectinload(User.devices).selectinload(relationship)

        statement = (
            select(User)
            .where(User.id == user_id)
            .options(
                readings_loader(Device.gps_readings, GPS),
                readings_loader(Device.gyroacc_readings, GyroAcc),
                readings_loader(Device.temphum_readings, TempHum),
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
