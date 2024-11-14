from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Habit
from auth.auth_bearer import verify_access_token
from schemas import HabitCreate
from utils import get_session

router = APIRouter()c 

@router.get("/habits")
def get_habits(
    user_id: int = Depends(verify_access_token),
    db: Session = Depends(get_session)
):
    
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    return habits

@router.post("/habit")
def create_habit(habit: HabitCreate, user_id: int = Depends(verify_access_token), db: Session = Depends(get_session)):
    print(habit)
    habit.user_id = user_id
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit