from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User as UserModel
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserSchema])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(UserModel).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = UserModel(
        first_name=payload.first_name,
        middle_name=payload.middle_name,
        last_name=payload.last_name,
        address=payload.address,
        phone_number=payload.phone_number,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    data = payload.model_dump(exclude_unset=True)
    # Since we used aliases (camelCase), ensure we access by field names
    for field, value in data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return None
