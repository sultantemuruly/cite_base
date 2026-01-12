from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
