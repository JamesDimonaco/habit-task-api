from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

class TokenTable(Base):
    __tablename__ = "tokens"

    user_id = Column(Integer, ForeignKey("users.id"))
    access_token = Column(String, primary_key=True)
    refresh_token = Column(String, nullable=False)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)
