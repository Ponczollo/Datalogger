from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import DB_SCHEMA, Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": DB_SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    devices: Mapped[list["Device"]] = relationship(
        secondary=f"{DB_SCHEMA}.user_device", back_populates="users"
    )
