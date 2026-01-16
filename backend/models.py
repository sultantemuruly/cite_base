from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from datetime import datetime


class User(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str

class Docs(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id")
    document_uuids: list[str] = Field(sa_column=Column(JSON))  # Chroma document UUIDs stored as JSON

