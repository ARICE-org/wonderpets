from typing import Optional
from jose import jwt
from fastapi import Cookie, Request, Response
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 5

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_ACCESS_TOKEN_EXPIRE_MINUTES

def create_token(data: dict, expires_minutes: int):
    # ensure required environment values are present to satisfy the type checker and runtime
    assert SECRET_KEY is not None, "JWT_SECRET_KEY is not set"
    assert ALGORITHM is not None, "JWT_ALGORITHM is not set"

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_auth_tokens(email: str):
    access_token = create_token({"sub": str(email)}, ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_token({"sub": str(email)}, 30*24*60*60)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}   

def store_token_in_cookie(response: Response, title: str, refresh_token: str, duration: int):
    response.set_cookie(key=title,
                        value=refresh_token, 
                        httponly=True, 
                        samesite="lax", 
                        max_age=duration)
    
def get_token_from_header_or_cookie(request: Request, access_token: Optional[str] = Cookie(None)) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1]
    return access_token