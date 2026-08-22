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

        experiment = db.query(Experiment).filter(
            Experiment.id == run.experiment_id
        ).first()
        
        if not experiment or experiment.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this run"
            )
        
        # 3. If status is success, fetch RunResult
        response_data = {
            "run_id": run.id,
            "experiment_id": run.experiment_id,
            "method": run.method,
            "status": run.status,
            "progress": run.progress,
            "created_at": run.created_at,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
            "error_message": run.error_message,
            "results": None
        }
        
        if run.status == "success":
            from app.models.run import RunResult
            
            run_result = db.query(RunResult).filter(
                RunResult.run_id == run_id
            ).first()
            
            if run_result:
                response_data["results"] = {
                    "observed_lift": run_result.observed_lift,
                    "p_value": run_result.p_value,
                    "z_statistic": run_result.z_statistic,
                    "ci_low": run_result.ci_low,
                    "ci_high": run_result.ci_high,
                    "significant": run_result.significant,
                    "summary": run_result.summary_json.get("summary") if run_result.summary_json else None,
                    "power_results": run_result.summary_json.get("power_results") if run_result.summary_json else None,
                    "charts": run_result.charts_json if run_result.charts_json else None
                }
        
        elif run.status == "failed":
            # Return error message
            response_data["error_message"] = run.error_message
        
        # 4. Return Run response
        from app.schemas.run import RunResponse
        return RunResponse(**response_data)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during database lookup")