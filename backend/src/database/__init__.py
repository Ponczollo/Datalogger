from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src import DB_USER, DB_HOST, DB_PASSWORD, DB_PORT, DB_NAME


DB_SCHEMA = "pzsp2"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(url=DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()
