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
