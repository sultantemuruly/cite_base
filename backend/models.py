from sqlmodel import Field, SQLModel, EmailStr


class User(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str
