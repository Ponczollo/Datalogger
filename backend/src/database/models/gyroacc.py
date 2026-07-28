from sqlalchemy import BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import DB_SCHEMA, Base


class GyroAcc(Base):
    __tablename__ = "gyroacc"
    __table_args__ = {"schema": DB_SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{DB_SCHEMA}.device.id"), nullable=False)
    time: Mapped[int] = mapped_column(BigInteger, nullable=True)
    gyro_x: Mapped[int] = mapped_column(Integer, nullable=True)
    gyro_y: Mapped[int] = mapped_column(Integer, nullable=True)
    gyro_z: Mapped[int] = mapped_column(Integer, nullable=True)
    acc_x: Mapped[int] = mapped_column(Integer, nullable=True)
    acc_y: Mapped[int] = mapped_column(Integer, nullable=True)
    acc_z: Mapped[int] = mapped_column(Integer, nullable=True)

    device: Mapped["Device"] = relationship(back_populates="gyroacc_readings")
