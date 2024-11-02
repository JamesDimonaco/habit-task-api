import schemas
from models import User, TokenTable
from database import Base, engine
from utils import create_access_token,create_refresh_token,verify_password,get_password_hash, get_session
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.auth_bearer import verify_refresh_token, verify_token

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_session)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    encrypted_password = get_password_hash(user.password)

    new_user = User(username=user.username, email=user.email, password=encrypted_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user": new_user}


@app.post("/login")
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
    

@app.get('/getusers')
def getusers(
    token: str = Depends(verify_token),
    db: Session = Depends(get_session)
):
    user = db.query(User).all()
    return user

@app.post("/change-password")
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

@app.post("/refresh-token")
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

@app.post("/logout")
def logout(
    token: str = Depends(verify_token),
    db: Session = Depends(get_session)
):
    token_db = db.query(TokenTable).filter(TokenTable.access_token == token).first()
    db.delete(token_db)
    db.commit()
    return {"message": "Logged out successfully"}

@app.get("/")
async def root():
    return {"message": "Hello World"}