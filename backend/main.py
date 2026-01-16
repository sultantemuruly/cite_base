import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db import create_db_and_tables
from routes import auth
from routes.documents import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (if needed)


app = FastAPI(lifespan=lifespan)

# Configure CORS - must be done before adding routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
)

# include routers
app.include_router(auth.router)
app.include_router(documents_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
