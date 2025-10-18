from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(digest)

def verify_password(plain_password: str, password: str) -> bool:
    digest = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(digest, password)
