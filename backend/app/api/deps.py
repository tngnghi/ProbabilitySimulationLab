from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.core.db import get_db
from typing import Generator
from app.models.user import User
from app.core.security import verify_access_token
from app.core.db import SessionLocal
from app.models import user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print(f"Token: {token}")

    try:
        payload = verify_access_token(token)
        print(f"Payload: {payload}")
        user_id = payload.get("user_id")
        print(f"User ID: {user_id}")
        if user_id is None:
            raise credentials_exception
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        print(f"Exception: {e}")
        raise credentials_exception