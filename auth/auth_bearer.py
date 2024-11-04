from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session
from utils import get_session
from models import TokenTable
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_session)
):
    try:
        decoded_token = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=["HS256"])
        
        expiry_timestamp = decoded_token.get("exp")
        current_timestamp = int(datetime.now().timestamp())

        user_id = decoded_token.get("user_id")


        has_expired = expiry_timestamp < current_timestamp        
        if has_expired:
            raise HTTPException(status_code=403, detail="Token expired.")
        
        token_db = db.query(TokenTable).filter(TokenTable.access_token == credentials.credentials).first()

        if not token_db:
            raise HTTPException(status_code=403, detail="Invalid token.")

        
        return user_id
    except Exception as e:
        print("Token verification failed:", str(e))
        raise HTTPException(status_code=403, detail="Token verification failed.")

def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_session),
):
    print("credentials:", credentials)
    try:
        decoded_token = jwt.decode(credentials.credentials, JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])        
        expiry_timestamp = decoded_token.get("exp")
        current_timestamp = int(datetime.now().timestamp())
        
        has_expired = expiry_timestamp < current_timestamp
        
        if has_expired:
            raise HTTPException(status_code=403, detail="Refresh token expired.")
        
        refresh_token_db = db.query(TokenTable).filter(TokenTable.refresh_token == credentials.credentials).first()
        if not refresh_token_db:
            raise HTTPException(status_code=403, detail="Invalid refresh token.")
            
        return credentials.credentials
    except Exception as e:
        print("Refresh token verification failed:", str(e))
        raise HTTPException(status_code=403, detail=str(e))
