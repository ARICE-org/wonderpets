from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Farmer
from app.schemas.farmer import FarmerBase
from app.schemas.user import UserInDB
from app.models.user import User
from app.middleware.useAuth import get_current_user

router = APIRouter(prefix="/user", tags=["Users"])

@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farmer = db.get(Farmer, current_user.user_id)
    if farmer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"email": current_user.email, "farmer": FarmerBase.model_validate(farmer)}

@router.get("/", response_model=List[UserInDB])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserInDB)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

