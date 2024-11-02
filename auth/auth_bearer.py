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

def verify_access_token(token: str, db: Session) -> bool:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        
        expiry_timestamp = decoded_token.get("exp")
        current_timestamp = int(datetime.now().timestamp())

        
        has_expired = expiry_timestamp < current_timestamp        
        if has_expired:
            raise HTTPException(status_code=403, detail="Token expired.")
        
        token_db = db.query(TokenTable).filter(TokenTable.access_token == token).first()
        
        return token_db is not None
    except Exception as e:
        print("Token verification failed:", str(e))
        return False

def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_session),
):
    print("credentials:", credentials)
    try:
        decoded_token = jwt.decode(credentials.credentials, JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
        print("Decoded refresh token:", decoded_token)
        
        expiry_timestamp = decoded_token.get("exp")
        current_timestamp = int(datetime.now().timestamp())
        
        print("Expiry timestamp:", expiry_timestamp)
        print("Current timestamp:", current_timestamp)
        
        has_expired = expiry_timestamp < current_timestamp
        print("Has expired:", has_expired)
        
        if has_expired:
            raise HTTPException(status_code=403, detail="Refresh token expired.")
        
        refresh_token_db = db.query(TokenTable).filter(TokenTable.refresh_token == credentials.credentials).first()
        if not refresh_token_db:
            raise HTTPException(status_code=403, detail="Invalid refresh token.")
            
        return credentials.credentials
    except Exception as e:
        print("Refresh token verification failed:", str(e))
        raise HTTPException(status_code=403, detail=str(e))

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_session),
):

    if not credentials:
        raise HTTPException(status_code=403, detail="Invalid authorization code.")
    
    if credentials.scheme != "Bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
    
    is_valid = verify_access_token(credentials.credentials, db)
    
    if not is_valid:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    
    return credentials.credentials