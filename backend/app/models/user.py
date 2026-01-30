from backend.app.core import db
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base



class User(Base) :
    __tablename__ = 'users'
    id = Column(UUID, primary_key=True, default = uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiments = relationship("Experiment", back_populates="user")

new_user = User(
    email="alice@example.com",
    password_hash="hashed_pw"
)
db.session.add(new_user)
db.session.commit()

user = db.session.query(User).filter(User.email == "alice@example.com").first()

experiments = user.experiments
print(experiments)

"""Lazy Loading vs Eager Loading: The Crucial Part
This is where (lazy-loaded) comes in.
Scenario
You fetch a user from the database:
pythonuser = db.query(User).filter(User.email == "alice@gmail.com").first()
Question: When you do user.experiments, does SQLAlchemy immediately fetch all her experiments, or wait until you ask for them?
Option A: Lazy Loading (default)
python# Query 1: Get user
user = db.query(User).filter(User.email == "alice@gmail.com").first()
print(f"Fetched user: {user.email}")  # Alice

# At this point, experiments are NOT fetched yet
# Database query 2 happens RIGHT HERE when you access .experiments
experiments = user.experiments  # <-- TRIGGER: Query fires NOW
print(f"User has {len(experiments)} experiments")  # [Exp101, Exp102]

# If you access again, it hits the database again (or cache if enabled)
for exp in user.experiments:  # <-- Another query!
    print(exp.name)
Pro: You only fetch data you actually use
Con: Extra database queries if you access multiple times; slower for large collections
Option B: Eager Loading (alternative)
python# Query 1: Get user AND experiments together
user = db.query(User).options(joinedload(User.experiments)).filter(
    User.email == "alice@gmail.com"
).first()

# Experiments already loaded! No extra query
experiments = user.experiments  # <-- No query, already in memory
print(f"User has {len(experiments)} experiments")

# Access again, still no query
for exp in user.experiments:  # <-- Still no query!
    print(exp.name)
Pro: One efficient query; multiple accesses are fast
Con: Fetches data you might not need; wastes memory/bandwidth
Visual Comparison
Lazy Loading:
Query 1: SELECT * FROM users WHERE email = 'alice@gmail.com'
         ↓ Returns User(id=1, email='alice@gmail.com')

(Later when you access user.experiments...)

Query 2: SELECT * FROM experiments WHERE user_id = 1
         ↓ Returns [Exp(101), Exp(102)]
Eager Loading:
Query 1: SELECT users.*, experiments.* 
         FROM users 
         LEFT JOIN experiments ON users.id = experiments.user_id 
         WHERE users.email = 'alice@gmail.com'
         ↓ Returns User + all Experiments in one go

When to Use Each
Use Lazy Loading (Default)

You're not sure if you'll use related data
You're fetching many users (don't want to load all their experiments)
Simple cases where you access relationships rarely

Example:
python# Listing users for dashboard (don't need experiments yet)
users = db.query(User).limit(10).all()
# Not accessing user.experiments, so lazy is perfect
Use Eager Loading

You know you'll need related data
You're displaying detailed info (user + their experiments)
Accessing relationship multiple times

Example:
python# Showing user details + all their experiments
user = db.query(User).options(joinedload(User.experiments)).get(1)
# Will access user.experiments multiple times, so eager is efficient

How It Connects to Your API
Example: Get Experiment Detail
python# Route in api/routes/experiments.py
@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    # Fetch experiment
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    # Access the linked user (lazy loading triggers here)
    owner = experiment.user  # <-- Implicit query
    
    # Return response
    return {
        "id": str(experiment.id),
        "name": experiment.name,
        "owner_email": owner.email  # Can access user properties
    }
In this case:

Query 1: Get experiment
Query 2 (implicit): Get user via experiment.user

If this happens 100 times in a loop, you get 100 queries (N+1 problem). Eager loading solves it.

Practical Code Example
Without Relationships (bad)
pythonclass User(Base):
    __tablename__ = "users"
    id: UUID = Column(UUID, primary_key=True)
    email: str = Column(String, unique=True)
    # No relationship defined

class Experiment(Base):
    __tablename__ = "experiments"
    id: UUID = Column(UUID, primary_key=True)
    user_id: UUID = Column(UUID, ForeignKey("users.id"))  # Foreign key exists
    name: str = Column(String)

# Usage
user = db.query(User).get(user_id)
# To get experiments, you must manually join
experiments = db.query(Experiment).filter(Experiment.user_id == user.id).all()
With Relationships (good)
pythonclass User(Base):
    __tablename__ = "users"
    id: UUID = Column(UUID, primary_key=True)
    email: str = Column(String, unique=True)
    
    # Relationship defined
    experiments = relationship("Experiment", back_populates="user")

class Experiment(Base):
    __tablename__ = "experiments"
    id: UUID = Column(UUID, primary_key=True)
    user_id: UUID = Column(UUID, ForeignKey("users.id"))
    name: str = Column(String)
    
    # Reverse relationship
    user = relationship("User", back_populates="experiments")

# Usage
user = db.query(User).get(user_id)
# Experiments accessed naturally
experiments = user.experiments  # Lazy loaded when accessed

Key Takeaway: What Does (lazy-loaded) Mean?
pythonexperiments: list of Experiment (lazy-loaded)
This means:

experiments: property name (not in database)
list of Experiment: it returns a list of Experiment objects
(lazy-loaded): the list is fetched from DB only when you access it, not when you fetch the User
If you never access user.experiments, no extra query is made


For Week 1: What You Actually Need to Know
You don't need to implement lazy vs eager loading yet. Just define:
pythonclass User(Base):
    __tablename__ = "users"
    id: UUID = Column(UUID, primary_key=True)
    email: str = Column(String, unique=True)
    password_hash: str = Column(String)
    created_at: DateTime = Column(DateTime, default=datetime.utcnow)
    
    # This line makes the magic work
    experiments = relationship("Experiment", back_populates="user")


Later (Week 3+), when you query, you'll naturally use lazy loading without thinking about it:
python# Get user
user = db.query(User).get(user_id)

# Access experiments (lazy loaded)
for exp in user.experiments:
    print(exp.name)

Summary Table
ConceptWhat It IsIn Database?When Loadeduser_id (FK)Foreign key column✅ YesAlwaysuser propertyLink to User object❌ NoWhen accessed (lazy)experiments propertyLink to Experiment list❌ NoWhen accessed (lazy)back_populatesBidirectional link❌ NoJust setup"""