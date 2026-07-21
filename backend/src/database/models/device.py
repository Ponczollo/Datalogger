from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import DB_SCHEMA, Base


class Device(Base):
    __tablename__ = "device"
    __table_args__ = {"schema": DB_SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[list["User"]] = relationship(
        secondary=f"{DB_SCHEMA}.user_device", back_populates="devices"
    )
    gps_readings: Mapped[list["GPS"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    gyroacc_readings: Mapped[list["GyroAcc"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    temphum_readings: Mapped[list["TempHum"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
