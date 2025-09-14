from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.user import UserInDB
from app.models.user import User
from app.utils.auth.jwt_token import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/user", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uuid: UUID = payload.get("sub")
        if uuid is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.uuid == uuid).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/", response_model=List[UserInDB])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    return {"id": current_user.uuid, "email": current_user.email, "role": "admin"}

@router.get("/{user_id}", response_model=UserInDB)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(User).get(user_id)

