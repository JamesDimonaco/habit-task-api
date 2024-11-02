import os 
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from dotenv import load_dotenv

from database import SessionLocal

# Load the environment variables
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "user_id": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "user_id": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

