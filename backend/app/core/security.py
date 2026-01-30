from  passlib.context import CryptContext
from jose import jwt 
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str :
    salt = pwd_context.gensalt()
    hashed = pwd_context.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool :
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    expiration_time = datetime.now(timezone.utc) + expires_delta
    return "n"