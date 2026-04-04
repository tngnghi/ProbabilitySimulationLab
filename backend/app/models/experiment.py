from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Integer, Enum, UUID
from app.core.db import Base
from sqlalchemy.orm import relationship

class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    alpha = Column(Float, default=0.05, nullable=False)
    two_sided = Column(Boolean, default=True, nullable=False)
    metric = Column(String, default="conversion", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="experiments")
    data = relationship("ExperimentData", back_populates="experiment", uselist=False, cascade="all, delete-orphan")
    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")

class ExperimentData(Base):
    __tablename__ = "experiment_data"
    
    experiment_id = Column(UUID, ForeignKey("experiments.id"), primary_key=True)
    n_a = Column(Integer, nullable=False)
    conv_a = Column(Integer, nullable=False)
    n_b = Column(Integer, nullable=False)
    conv_b = Column(Integer, nullable=False)
    data_source = Column(Enum("aggregate", "events", name="data_source_enum"), nullable=False, default="aggregate")
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)

    experiment = relationship("Experiment", back_populates="data", uselist=False)
