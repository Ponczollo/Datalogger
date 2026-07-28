from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import DB_SCHEMA, Base


class GPS(Base):
    __tablename__ = "gps"
    __table_args__ = {"schema": DB_SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{DB_SCHEMA}.device.id"), nullable=False)
    time: Mapped[int] = mapped_column(BigInteger, nullable=True)
    sentence: Mapped[str] = mapped_column(String(255), nullable=False)

    device: Mapped["Device"] = relationship(back_populates="gps_readings")
