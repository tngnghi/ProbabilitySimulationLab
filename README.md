# ProbabilitySimulationLab

A full-stack web platform for running statistical experiments, A/B tests, and simulation-based inference — built as an independent personal project.

## What It Does

- Create and manage **A/B testing experiments** with configurable alpha, metric, and test type
- Upload aggregate conversion data (group size + conversions) per experiment
- Run **statistical analyses**: two-proportion z-test with p-value, confidence interval, observed lift, and significance verdict
- Get plain-English AI-generated summaries of results
- Full **user auth** with JWT — each user owns their experiments

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy ORM |
| Auth | JWT (python-jose + bcrypt) |
| Migrations | Alembic |
| Containerization | Docker + Docker Compose |
| Statistics | SciPy, NumPy |

## Architecture
frontend/         # (in progress)
backend/
app/
api/routes/   # REST endpoints: auth, experiments, runs
models/       # SQLAlchemy ORM: User, Experiment, ExperimentData, Run, RunResult
schemas/      # Pydantic request/response validation
services/     # stats.py (z-test), validations.py
core/         # config, db session, security (JWT)
alembic/        # DB migration history
docker-compose.yml
## API Highlights

- `POST /auth/register` / `POST /auth/login` — user registration & token issuance
- `POST /experiments` — create a named experiment with configurable alpha & metric
- `POST /experiments/{id}/data/aggregate` — upload A/B group data
- `POST /experiments/{id}/runs` — run z-test analysis
- `GET /experiments` — list all experiments for the authenticated user

## Running Locally

```bash
cp backend/.env.example backend/.env
# Fill in your DB credentials and JWT secret

docker-compose up --build
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Status

🚧 Active development — frontend and permutation test method in progress.
