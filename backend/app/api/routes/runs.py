from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import uuid4
from datetime import datetime

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.models.experiment import Experiment, ExperimentData
from app.models.run import Run
from app.schemas.run import RunCreate, RunResponse
from app.services.tasks import run_analysis_task
from uuid import UUID

router = APIRouter()

@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 1. Manually convert string to UUID to validate format
        uuid_obj = UUID(run_id)
        
        # 2. Query using the UUID object
        run = (
            db.query(Run)
            .options(joinedload(Run.results))
            .filter(Run.id == uuid_obj)
            .first()
        )
    
        if not run:
            print(f"ID {run_id} not found in database.")
            raise HTTPException(status_code=404, detail="Run record not found in database.")

        return run
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during database lookup")