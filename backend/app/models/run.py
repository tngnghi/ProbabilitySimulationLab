from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Integer, Enum, UUID, JSON
from app.core.db import Base
from sqlalchemy.orm import relationship

class Run(Base):
    __tablename__ = "runs"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    experiment_id = Column(UUID, ForeignKey("experiments.id"), nullable=False)
    method = Column(Enum("ztest", "permutation", name="run_method"), nullable=False, )
    n_sim = Column(Integer, default=20000, nullable=True)
    seed = Column(Integer, nullable=True)
    status = Column(Enum("queued", "running", "success", "failed", name="run_status"), default="queued")
    progress = Column(Float, default=0.0, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    experiment = relationship("Experiment", back_populates="runs")
    results = relationship("RunResult", uselist=False, back_populates="run", cascade="all, delete-orphan")

class RunResult(Base):
    __tablename__ = "run_results"

    run_id = Column(UUID, ForeignKey("runs.id"), primary_key = True)
    observed_lift = Column(Float, nullable=False)
    p_value = Column(Float, default=0.0, nullable=False)
    z_statistic = Column(Float, nullable=True)
    ci_low = Column(Float, nullable=True)
    ci_high = Column(Float, nullable=True)
    significant = Column(Boolean)
    summary_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="results")
    """The RunResult Model (For Later: Week 8)
pythonclass RunResult(Base):
    
    power_json = Column(JSON, nullable=True)
    charts_json = Column(JSON, nullable=True)
Key columns:

observed_lift: The actual difference you saw (e.g., 0.125 = 12.5% lift)
p_value: Statistical significance (e.g., 0.032)
ci_*: Confidence interval bounds (e.g., between 0.10 and 0.15)
*_json: Store complex data as JSON

power_json: {effect_grid: [...], power: [...]}
charts_json: Plotly-ready arrays for visualization

"""