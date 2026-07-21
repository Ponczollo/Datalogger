from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import DB_SCHEMA, Base


class TempHum(Base):
    __tablename__ = "temphum"
    __table_args__ = {"schema": DB_SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{DB_SCHEMA}.device.id"), nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=True)
    temperature: Mapped[int] = mapped_column(Integer, nullable=True)
    humidity: Mapped[int] = mapped_column(Integer, nullable=True)

    device: Mapped["Device"] = relationship(back_populates="temphum_readings")
