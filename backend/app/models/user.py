from sqlalchemy import Column, String, DateTime, UUID
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

from app.models import Base



class User(Base) :
    __tablename__ = 'users'
    id = Column(UUID, primary_key=True, default = uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    experiments = relationship("Experiment", back_populates="user", cascade="all, delete-orphan")