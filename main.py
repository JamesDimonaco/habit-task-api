from routers import habits
import schemas
from models import User, TokenTable
from database import Base, engine
from utils import create_access_token,create_refresh_token,verify_password,get_password_hash, get_session
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.auth_bearer import verify_refresh_token, verify_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add prefix for all routes
api_router = FastAPI()

# Move all existing routes to api_router
@api_router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_session)):
    print("user", user)
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    encrypted_password = get_password_hash(user.password)
    try:
        new_user = User(username=user.username, email=user.email, password=encrypted_password)
        print(new_user)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        access_token = create_access_token(new_user.id)
        refresh_token = create_refresh_token(new_user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@api_router.post("/login")
def login_user(requestUser: schemas.requestDetails, db: Session = Depends(get_session)):
    existing_user = db.query(User).filter(User.email == requestUser.email).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    hashed_password = existing_user.password
    if not verify_password(requestUser.password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    access_token = create_access_token(existing_user.id)
    refresh_token = create_refresh_token(existing_user.id)

    token_db = TokenTable(user_id=existing_user.id, access_token=access_token, refresh_token=refresh_token, status=True)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {"access_token": access_token, "refresh_token": refresh_token}
    

@api_router.get('/getusers')
def getusers(
    user_id: int = Depends(verify_access_token),
    db: Session = Depends(get_session)
):
    user = db.query(User).all()
    return user

@api_router.get('/user')
def getuser(
    user_id: int = Depends(verify_access_token),
    db: Session = Depends(get_session)
):
    user = db.query(User).filter(User.id == user_id).first()
    return user

@api_router.post("/change-password")
def change_password(request: schemas.changePassword, db: Session = Depends(get_session)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if not verify_password(request.old_password, existing_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    encrypted_password = get_password_hash(request.new_password)
    existing_user.password = encrypted_password
    db.commit()
    db.refresh(existing_user)
    return {"message": "Password changed successfully"}

@api_router.post("/refresh-token")
def refresh_token(
    db: Session = Depends(get_session),
    token: str = Depends(verify_refresh_token)
):
    token_db = db.query(TokenTable).filter(TokenTable.refresh_token == token).first()
    if not token_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")
    
    access_token = create_access_token(token_db.user_id)
    refresh_token = create_refresh_token(token_db.user_id)

    token_db.access_token = access_token
    token_db.refresh_token = refresh_token
    db.commit()
    db.refresh(token_db)
    return {"access_token": access_token, "refresh_token": refresh_token}

@api_router.post("/logout")
def logout(
    user_id: int = Depends(verify_access_token),
    db: Session = Depends(get_session)
):
    token_db = db.query(TokenTable).filter(TokenTable.user_id == user_id).all() 
    for token in token_db:
        db.delete(token)
        db.commit()
    return {"message": "Logged out successfully"}

@api_router.get("/")
async def root():
    return {"message": "Hello World"}

# Mount the API router with prefix
app.mount("/api", api_router)

# Include the habits router with the api prefix
api_router.include_router(habits.router)
