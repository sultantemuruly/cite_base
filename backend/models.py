from sqlmodel import Field, SQLModel
from datetime import datetime


class User(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str


class Docs(SQLModel, table=True):
    docs_id: int | None = Field(default=None, index=True, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    document_uuid: str = Field(index=True)  # Chroma document UUID
    created_at: datetime = Field(default_factory=datetime.now)
