import os
from dotenv import load_dotenv

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

sqlite_url = os.getenv("DATABASE_URL")

if not sqlite_url:
    raise ValueError("DATABASE_URL environment variable not set")

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
