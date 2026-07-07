import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from psycopg2 import IntegrityError
from app.models.user import User
from app.api.deps import get_current_user, get_db
from app.schemas.auth import UserResponse
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.api.routes import experiments, runs
from app.core.config import settings
import logging
from app.api.deps import get_current_user, get_db

import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


class PrettyJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            default=str,
        ).encode("utf-8")


app = FastAPI(
    title="Probability Simulation Lab",
    default_response_class=PrettyJSONResponse,
)

origins = [
    "http://localhost:3000",          # local dev
    "https://probsimlab.vercel.app/",  # production Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],          # allows OPTIONS, GET, POST, etc.
    allow_headers=["*"],          # allows Authorization, Content-Type
)

if __name__ == '__main__':
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, workers=4)
logger = logging.getLogger(__name__)

#Auth
@app.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):    
    try:
        existing_user = db.query(User).filter(User.email == payload.email).first()        
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = hash_password(payload.password)
        new_user = User(email=payload.email, password_hash=hashed_password)
        db.add(new_user)        
        db.commit()        
        db.refresh(new_user)
        
        response = UserResponse.from_orm(new_user)
        return response
        
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during registration: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"user_id": user.id, "email": user.email})
    return TokenResponse(access_token=token, token_type="bearer")

@app.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

#Experiments
app.include_router(experiments.router)
app.include_router(runs.router)

# Health check
@app.get("/health", status_code=200)
async def health_check():
    is_healthy = True
    if not is_healthy:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    environment = settings.env_name
    return {
        "status": "healthy",
         "environment": environment
    }
