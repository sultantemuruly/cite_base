from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import Session
from db import get_session
from routes.auth import verify_token
from models import User

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    email: str = Depends(verify_token),
    db_session: SessionDep,
) -> User:
    """Get the current authenticated user from JWT token."""
    user = db_session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
