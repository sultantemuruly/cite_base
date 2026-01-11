import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import JWTError, jwt

from dependencies import SessionDep
from db import create_db_and_tables
from models import User

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise ValueError("SECRET_KEY environment variable not set")

algorithm = os.getenv("ALGORITHM")
if not algorithm:
    raise ValueError("ALGORITHM environment variable not set")

access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: EmailStr
    password: str


def get_user_by_email(email: str, db_session: SessionDep):
    return db_session.query(User).filter(User.email == email).first()


def create_user(user: UserCreate, db_session: SessionDep):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/users/register")
def register(user: UserCreate, session: SessionDep):
    db_user = get_user_by_email(user.email, session)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = create_user(user, session)
    return {"id": created_user.id, "email": created_user.email}


def authenticate_user(email: str, password: str, db_session: SessionDep):
    user = get_user_by_email(email, db_session)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


@app.post("/users/token")
def login_for_access_token(
    db_session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(form_data.username, form_data.password, db_session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expire = timedelta(minutes=access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expire
    )
    return {"access_token": access_token, "token_type": "bearer"}


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


@app.post("/users/verify_token")
async def verify_user_token(token: str = Depends(oauth2_scheme)):
    email = verify_token(token)
    return {"email": email}
