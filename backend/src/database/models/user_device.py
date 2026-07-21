from sqlalchemy import Column, ForeignKey, Integer, Table

from src.database import Base, DB_SCHEMA

user_device = Table(
    "user_device",
    Base.metadata,
    Column("user_id", Integer, ForeignKey(f"{DB_SCHEMA}.user.id"), primary_key=True),
    Column("device_id", Integer, ForeignKey(f"{DB_SCHEMA}.device.id"), primary_key=True),
    schema=DB_SCHEMA,
)
