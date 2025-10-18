from typing import Optional
from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError
import jwt
from sqlalchemy.orm import Session

from app.utils.auth.jwt_token import SECRET_KEY, ALGORITHM, get_token_from_header_or_cookie
from app.dependencies import get_db
from app.models.user import User

def get_current_user(access_token: Optional[str] = Depends(get_token_from_header_or_cookie), db: Session = Depends(get_db)):
    if(access_token is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated")
    
    try:
        assert SECRET_KEY is not None, "JWT_SECRET_KEY is not set"
        assert ALGORITHM is not None, "JWT_ALGORITHM is not set"

        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user