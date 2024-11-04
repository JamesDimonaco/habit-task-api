from pydantic import BaseModel
import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class requestDetails(BaseModel):
    email: str
    password: str
class changePassword(BaseModel):
    email: str
    old_password: str
    new_password: str

class HabitCreate(BaseModel):
    name: str
    description: str
    user_id: int


