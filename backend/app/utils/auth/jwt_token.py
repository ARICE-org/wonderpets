from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_token(data: dict, expires_minutes: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_auth_tokens(user_id: str, role: str):
    access_token = create_token({"sub": str(user_id), "role": role}, ACCESS_TOKEN_EXPIRE_MINUTES)
    # refresh_token = create_token({"sub": str(user_id), "role": role}, 60*24*30)
    return {"access_token": access_token, "token_type": "bearer"}
    # return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
