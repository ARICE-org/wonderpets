import os
from typing import Optional
from fastapi import APIRouter, Cookie, Response, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
import jwt
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.user import UserCreate
from app.models.user import User
from app.utils.auth.email_checker import is_valid_email, error_message as email_errors
from app.utils.auth.jwt_token import create_auth_tokens
from app.utils.auth.password_checker import is_valid_password, error_message as password_errors
from app.utils.auth.password_hashing import hash_password, verify_password
from app.utils.auth.jwt_token import store_token_in_cookie

router = APIRouter(prefix="/auth", tags=["Auth"])

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(form_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == form_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Email already registered"])

    if form_data.email == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=["Username not provided"])

    if form_data.password == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=["Password not provided"])

    if not is_valid_email(form_data.email):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=email_errors)

    if not is_valid_password(form_data.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=password_errors)

    user = User(
        email=form_data.email,
        password=hash_password(form_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_auth_tokens(form_data.email)
    store_token_in_cookie(response,ACCESS_COOKIE_NAME, token["access_token"], 60)
    store_token_in_cookie(response,REFRESH_COOKIE_NAME, token["refresh_token"], 30*24*60*60)

    return token["access_token"]

@router.post("/login",  status_code=status.HTTP_201_CREATED)
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    if form_data.username == "" :
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username not provided")

    if form_data.password == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username not provided")

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, str(user.password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_auth_tokens(str(user.email))
    store_token_in_cookie(response,ACCESS_COOKIE_NAME, token["access_token"], 60)
    store_token_in_cookie(response,REFRESH_COOKIE_NAME, token["refresh_token"], 30*24*60*60)

    return {"access_token": token["access_token"], "token_type": "bearer"}

@router.post("/refresh", status_code=status.HTTP_201_CREATED)
def refresh_token(response: Response, db: Session = Depends(get_db), refresh_token: Optional[str] = Cookie(None)):
    try:
        assert refresh_token is not None, "No refresh token provided"
        assert SECRET_KEY is not None, "JWT_SECRET_KEY is not set"
        assert ALGORITHM is not None, "JWT_ALGORITHM is not set"

        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    token = create_auth_tokens(str(user.email))
    store_token_in_cookie(response,"refresh_token", token["refresh_token"], 30*24*60*60)
    store_token_in_cookie(response,"access_token", token["access_token"], 60)

    return {"access_token": token["access_token"], "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}
