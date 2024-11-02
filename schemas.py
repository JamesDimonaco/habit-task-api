from pydantic import BaseModel
import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class TokenStatus(BaseModel):
    status: str

class requestDetails(BaseModel):
    email: str
    password: str

class TokenCreate(BaseModel):
    access_token: str
    refresh_token: str
    status: bool
    created_at: datetime.datetime
    user_id: int

class changePassword(BaseModel):
    email: str
    old_password: str
    new_password: str
