from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from backend.app.core import db
from app.models import Base

class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    alpha = Column(Float, default=0.05)
    two_sided = Column(Boolean, default=True)
    metric = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # LINK to User model
    user = relationship("User", back_populates="experiments")

user = db.session.query(Experiment).filter(Experiment.id == "xyz1").first()

owner = exp.user
print(owner.email)

class ExperimentData(Base):
    __tablename__ = "experiment_data"
    
    experiment_id = Column(UUID, ForeignKey("experiments.id"), primary_key=True)
    n_a = Column(Integer, nullable=False)
    conv_a = Column(Integer, nullable=False)
    n_b = Column(Integer, nullable=False)
    conv_b = Column(Integer, nullable=False)
    data_source = Column(Enum, default="aggregate")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

"""
please find this in option a: {"detail":"Not Found"}. continue week 1 the rest of action, skeleton not code yet, just explain<2>
Can you explain this section to me in more detail? <1>

The Run Model (For Later: Week 6)
pythonclass Run(Base):
    __tablename__ = "runs"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    experiment_id = Column(UUID, ForeignKey("experiments.id"), nullable=False)
    method = Column(String, nullable=False)  # "ztest" or "permutation"
    n_sim = Column(Integer, default=20000)
    seed = Column(Integer, nullable=True)
    status = Column(String, default="queued")  # queued, running, success, failed
    progress = Column(Float, default=0.0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
Key columns:

method: Which test you ran (z-test vs permutation)
status: Track progress (queued → running → success)
progress: 0.0 to 1.0 (0% to 100% done)
started_at, finished_at: Track timing

Why track these?

Frontend polls: "Is my run done yet?" (checks status)
Shows progress bar (checks progress)
If failed, shows error (error_message)


The RunResult Model (For Later: Week 8)
pythonclass RunResult(Base):
    __tablename__ = "run_results"
    
    run_id = Column(UUID, ForeignKey("runs.id"), primary_key=True)
    observed_lift = Column(Float, nullable=False)
    p_value = Column(Float, nullable=False)
    ci_low = Column(Float, nullable=True)
    ci_high = Column(Float, nullable=True)
    power_json = Column(JSON, nullable=True)
    charts_json = Column(JSON, nullable=True)
    summary_json = Column(JSON, nullable=True)
Key columns:

observed_lift: The actual difference you saw (e.g., 0.125 = 12.5% lift)
p_value: Statistical significance (e.g., 0.032)
ci_*: Confidence interval bounds (e.g., between 0.10 and 0.15)
*_json: Store complex data as JSON

power_json: {effect_grid: [...], power: [...]}
charts_json: Plotly-ready arrays for visualization



Why JSON?

Not all data fits in simple columns
Power analysis produces arrays (effect sizes, power values)
Store as JSON, retrieve as JSON, pass directly to frontend


How These All Connect
Visual relationship diagram:
One User ──────┐
               │ (one-to-many)
        Has Many Experiments
               │
        Each Experiment ──────┐
                              │ (one-to-one)
                        Has One ExperimentData
                              │
                              ├─ n_a, conv_a, n_b, conv_b
                              │
                        Has Many Runs
                              │
                        Each Run ──────┐
                                       │ (one-to-one)
                                Has One RunResult
                                       │
                                       ├─ p_value, lift
                                       ├─ power_json
                                       └─ charts_json
In SQL terms (foreign keys):
users.id
   ↓
experiments.user_id → users.id
   ↓
experiment_data.experiment_id → experiments.id
   ↓
runs.experiment_id → experiments.id
   ↓
run_results.run_id → runs.id

From Model to Database: Migration
You write:
pythonclass User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
Alembic generates (Week 1, Step 4):
sqlCREATE TABLE users (
    id UUID NOT NULL,
    email VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (email)
);
You run:
bashalembic upgrade head
Database now has the users table, ready to store data.

Usage in Code: Examples
Creating a User
pythonfrom app.models.user import User
from uuid import uuid4

new_user = User(
    id=uuid4(),
    email="alice@example.com",
    password_hash="$2b$12$..."  # bcrypt hash
)
# created_at auto-set to current time
Querying a User
pythonfrom sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

user = get_user_by_email(db, "alice@example.com")
print(user.id, user.email)
Creating an Experiment for a User
pythonfrom app.models.experiment import Experiment

exp = Experiment(
    id=uuid4(),
    user_id=user.id,  # Link to user
    name="Button Color Test",
    description="A/B test blue vs red CTA",
    alpha=0.05,
    two_sided=True,
    metric="conversion"
)
# created_at auto-set
Accessing Related Data
python# Get all experiments for a user (uses relationship)
user.experiments  # List of Experiment objects

# Get the user who owns an experiment (uses foreign key)
exp = db.query(Experiment).first()
owner = exp.user  # Automatically fetches User
print(owner.email)

Key Takeaways
ConceptExamplePurposeClassclass User(Base)Represents a table__tablename__"users"Database table nameColumnid = Column(UUID, ...)Table columnPrimary Keyprimary_key=TrueUnique identifier for each rowForeign KeyForeignKey("users.id")Link to another tableDefaultdefault=uuid4Auto-fill if not providedNullablenullable=FalseRequired vs optionalUniqueunique=TrueNo duplicates allowedJSONColumn(JSON)Store complex data
Remember: Each model class = one table. Each attribute = one column. Each instance = one row."""