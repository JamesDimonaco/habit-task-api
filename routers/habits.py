from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth.auth_bearer import verify_token
from utils import get_session

router = APIRouter()

@router.get("/habits")
def get_habits(
    user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    print(user_id)
    return {"message": "Hello, World!"}