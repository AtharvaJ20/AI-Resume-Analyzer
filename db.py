from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set. Add it to your .env file.")

connect_args = {}
ssl_ca = os.environ.get("DB_SSL_CA")
if ssl_ca:
    connect_args["ssl"] = {"ca": ssl_ca}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
