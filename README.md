# Probability Simulation Lab

An in-progress full-stack platform for managing A/B testing experiments and running statistical inference on aggregated conversion data.

## What It Does

- Create and manage **A/B testing experiments** with configurable alpha, metric, and test type
- Upload aggregate conversion data (group size + conversions) per experiment
- Run **statistical analyses**: two-proportion z-test with p-value, confidence interval, observed lift, and significance verdict
- Get plain-English statistical summaries of results
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
```
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
```
## API Highlights

- `POST /auth/register` — create a new user
- `POST /auth/login` — authenticate user and return JWT token
- `GET /me` — return the authenticated user
- `POST /experiments` — create a named experiment
- `GET /experiments` — list experiments owned by the authenticated user
- `GET /experiments/{id}` — retrieve one experiment
- `PATCH /experiments/{id}` — update experiment metadata
- `DELETE /experiments/{id}` — delete an experiment
- `POST /experiments/{id}/data/aggregate` — upload aggregated A/B test data

 In progress:
- `POST /experiments/{id}/runs` — execute and store analysis runs

## Statistical Analysis

The current statistical workflow implements a two-proportion z-test for comparing conversion rates between variants A and B.

Given aggregated conversion data:
```json
{
  "n_a": 1000,
  "conv_a": 80,
  "n_b": 1000,
  "conv_b": 105
}
```
The analysis computes:

- Conversion rate for group A
- Conversion rate for group B
- Observed lift
- Z-statistic
- P-value
- Confidence interval
- Significance verdict based on the experiment alpha

Example result shape:
```json
{
  "observed_lift":0.31055900621118016,
  "p_value":0.05391604210018319,
  "z_statistic":1.9275104894106296,
  "ci_low":0.08636275484039944,
  "ci_high":0.12442645594881134,
  "significant":false,
  "summary":"No significant difference detected (p=0.054, lift=31.1%)"
}
```
## Running Locally

```bash
cp backend/.env.example backend/.env
# Fill in your DB credentials and JWT secret

docker-compose up --build
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```
## Project Status

Active development.

Completed:

- FastAPI backend setup
- PostgreSQL database integration
- SQLAlchemy models and Alembic migrations
- JWT authentication
- Protected routes
- User-specific experiment access
- Experiment CRUD APIs
- Aggregated data validation
- Two-proportion z-test implementation

In progress:

- Analysis run endpoint for storing z-test results
- Simulation-based permutation testing
- Power simulation across different effect sizes
- Minimal React frontend dashboard
- Deployment
