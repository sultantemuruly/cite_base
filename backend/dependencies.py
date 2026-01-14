import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from jose import JWTError, jwt
from db import get_session
from models import User

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise ValueError("SECRET_KEY environment variable not set")

algorithm = os.getenv("ALGORITHM")
if not algorithm:
    raise ValueError("ALGORITHM environment variable not set")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

SessionDep = Annotated[Session, Depends(get_session)]


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid")


def get_current_user(
    db_session: SessionDep,
    email: str = Depends(verify_token),
) -> User:
    """Get the current authenticated user from JWT token."""
    user = db_session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
