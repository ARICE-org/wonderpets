import jwt
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.user import UserBase, UserCreate
from app.models.user import User
from app.utils.auth.email_checker import is_valid_email, error_message as email_errors
from app.utils.auth.jwt_token import create_auth_tokens, SECRET_KEY, ALGORITHM
from app.utils.auth.password_checker import is_valid_password, error_message as password_errors
from app.utils.auth.password_hashing import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(form_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == form_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Email already registered"])

    if form_data.email == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=["Username not provided"])

    if form_data.hashed_password == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=["Password not provided"])

    if not is_valid_email(form_data.email):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=email_errors)

    if not is_valid_password(form_data.hashed_password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=password_errors)

    user = User(
        email=form_data.email,
        hashed_password=hash_password(form_data.hashed_password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_auth_tokens(user.uuid, role="admin")
    return token

@router.post("/login",  status_code=status.HTTP_201_CREATED)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    if form_data.username == "" :
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username not provided")

    if form_data.password == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username not provided")

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_auth_tokens(user.uuid, role="admin")
    return token
