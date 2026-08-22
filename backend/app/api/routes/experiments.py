from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.experiment import ExperimentDataResponse, ExperimentResponse, ExperimentUpdate, ExperimentCreate, ExperimentDataCreate, ExperimentDataUpdate
from app.models.experiment import Experiment, ExperimentData
from app.schemas.run import RunCreate, RunResponse, RunResultResponse
from app.models.run import Run, RunResult
from app.services.stats import z_test_two_proportions
from sqlalchemy.orm import Session, joinedload
from app.services.validations import validate_aggregated_data
from app.services.tasks import run_analysis_task
from uuid import uuid4, UUID

router = APIRouter(prefix="/experiments", tags=["experiments"])

@router.post("", status_code=201, response_model=ExperimentResponse)
async def create_experiment(experiment_data: ExperimentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_experiment = Experiment(
        id=uuid4(),
        user_id=current_user.id,
        name=experiment_data.name,
        description=experiment_data.description,
        alpha=experiment_data.alpha,
        two_sided=experiment_data.two_sided,
        metric=experiment_data.metric,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    existing_name = db.query(Experiment).filter(Experiment.user_id == current_user.id, Experiment.name == experiment_data.name).first()

    if existing_name:
        raise HTTPException(status_code=400, detail="Experiment name already exists for this user")
    db.add(new_experiment)
    db.commit()
    db.refresh(new_experiment)
    return ExperimentResponse.from_orm(new_experiment)


@router.get("", response_model=List[ExperimentResponse])
async def list_experiments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    experiments = db.query(Experiment).filter(Experiment.user_id == current_user.id).options(joinedload(Experiment.data)).order_by(Experiment.created_at.desc()).offset(skip).limit(limit).all()
    return [ExperimentResponse.from_orm(exp) for exp in experiments]


@router.get("/{experiment_id}", response_model=ExperimentResponse, status_code=200)
async def get_experiment(experiment_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).options(joinedload(Experiment.data)).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    data_dict = None
    if experiment.data:
        data_dict = {
            "n_a": experiment.data.n_a,
            "conv_a": experiment.data.conv_a,
            "n_b": experiment.data.n_b,
            "conv_b": experiment.data.conv_b,
            "data_source": experiment.data.data_source,
            "updated_at": experiment.data.updated_at
        }
    
    return ExperimentResponse(
        id=experiment.id,
        user_id=experiment.user_id,
        name=experiment.name,
        description=experiment.description,
        alpha=experiment.alpha,
        two_sided=experiment.two_sided,
        metric=experiment.metric,
        created_at=experiment.created_at,
        updated_at=experiment.updated_at,
        data=data_dict
    )


@router.patch("/{experiment_id}", response_model=ExperimentResponse, status_code=200)
async def update_experiment(experiment_id: UUID, update_data:ExperimentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Check for name conflict
    if update_data.name is not None:
    # Check if another experiment has this name
        existing_name = db.query(Experiment).filter(Experiment.user_id == current_user.id, Experiment.name == update_data.name, Experiment.id != experiment_id).first()
        if existing_name:
            raise HTTPException(status_code=400, detail="Experiment name already exists for this user")
        experiment.name = update_data.name
    # Update fields
    if update_data.name is not None:
        experiment.name = update_data.name
    if update_data.description is not None:
        experiment.description = update_data.description
    if update_data.alpha is not None:
        if update_data.alpha <= 0 or update_data.alpha >= 1:
            raise HTTPException(status_code=422, detail="Alpha must be between 0 and 1")
        experiment.alpha = update_data.alpha
    if update_data.two_sided is not None:
        experiment.two_sided = update_data.two_sided
    if update_data.metric is not None:
        experiment.metric = update_data.metric

    experiment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(experiment)
    data_dict = None
    if experiment.data:
        data_dict = {
            "n_a": experiment.data.n_a,
            "conv_a": experiment.data.conv_a,
            "n_b": experiment.data.n_b,
            "conv_b": experiment.data.conv_b,
            "data_source": experiment.data.data_source,
            "updated_at": experiment.data.updated_at
        }
        
    return ExperimentResponse(id=experiment.id,
        user_id=experiment.user_id,
        name=experiment.name,
        description=experiment.description,
        alpha=experiment.alpha,
        two_sided=experiment.two_sided,
        metric=experiment.metric,
        created_at=experiment.created_at,
        updated_at=experiment.updated_at,
        data=data_dict
        )


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(experiment_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if experiment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this experiment")
    db.delete(experiment)
    db.commit()

@router.post("/{experiment_id}/data/aggregate", response_model=ExperimentDataResponse, status_code=201)
async def upload_experiment_data(experiment_id: UUID, data: ExperimentDataCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # Verify experiment exists and belongs to user
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Validate data BEFORE using
    if data.n_a <= 0 or data.n_b <= 0:
        raise HTTPException(status_code=422, detail="n_a and n_b must be > 0")
    if data.conv_a < 0 or data.conv_b < 0:
        raise HTTPException(status_code=422, detail="Conversions cannot be negative")
    if data.conv_a > data.n_a or data.conv_b > data.n_b:
        raise HTTPException(status_code=422, detail="Conversions cannot exceed samples")
    
    warnings_list = validate_aggregated_data(data.n_a, data.conv_a, data.n_b, data.conv_b)
    
    # Check if data exists
    existing_data = (db.query(ExperimentData).filter(ExperimentData.experiment_id == experiment_id).first())
    
    if existing_data:
        # Update
        existing_data.n_a = data.n_a
        existing_data.conv_a = data.conv_a
        existing_data.n_b = data.n_b
        existing_data.conv_b = data.conv_b
        existing_data.updated_at = datetime.now(timezone.utc)
    else:
        # Create
        new_data = ExperimentData(
            experiment_id=experiment_id,
            n_a=data.n_a,
            conv_a=data.conv_a,
            n_b=data.n_b,
            conv_b=data.conv_b,
            data_source="aggregate",
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_data)
        existing_data = new_data
    
    db.commit()
    db.refresh(existing_data)
    
    # Fetch and return
    existing_data.warnings = warnings_list
    
    return ExperimentDataResponse.from_orm(existing_data)

@router.get("/{experiment_id}/data", response_model=ExperimentDataResponse, status_code=200)
async def access_experiment_data(experiment_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    existing_data = db.query(ExperimentData).filter(ExperimentData.experiment_id == experiment_id).first()
    if not existing_data:
        raise HTTPException(status_code=204, detail="No Content (empty)")

    return ExperimentDataResponse.from_orm(existing_data)

@router.patch("/{experiment_id}/data", response_model=ExperimentDataResponse, status_code=200)
async def update_experiment_data(experiment_id: UUID, update_data:ExperimentDataUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiments = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).first()
    if not experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    existing_data = (
        db.query(ExperimentData)
        .filter(ExperimentData.experiment_id == experiment_id)
        .first()
    )

    if not existing_data:
        raise HTTPException(status_code=404, detail="Experiment data not found")

    if update_data.n_a is not None:
        if update_data.n_a <= 0:
            raise HTTPException(status_code=422, detail="n_a must be > 0")
        existing_data.n_a = update_data.n_a
    if update_data.n_b is not None:
        if update_data.n_b <= 0:
            raise HTTPException(status_code=422, detail="n_b must be > 0")
        existing_data.n_b = update_data.n_b
    if update_data.conv_a is not None:
        if update_data.conv_a < 0:
            raise HTTPException(status_code=422, detail="Conversions cannot be negative")
        existing_data.conv_a = update_data.conv_a
    if update_data.conv_b is not None:
        if update_data.conv_b < 0:
            raise HTTPException(status_code=422, detail="Conversions cannot be negative")
        existing_data.conv_b = update_data.conv_b
    if existing_data.conv_a > existing_data.n_a or existing_data.conv_b > existing_data.n_b:
        raise HTTPException(status_code=422, detail="Conversions cannot exceed samples")

    warnings_list = validate_aggregated_data(existing_data.n_a, existing_data.conv_a, existing_data.n_b, existing_data.conv_b)

    existing_data.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(existing_data)

    existing_data.warnings = warnings_list
    
    return ExperimentDataResponse.from_orm(existing_data)

@router.post("/{experiment_id}/runs", response_model=RunResponse, status_code=201)
async def create_run(
    experiment_id: UUID,
    run_req: RunCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if run_req.method not in ["ztest", "permutation"]:
        raise HTTPException(
            status_code=422,
            detail="method must be 'ztest' or 'permutation'"
        )
    
    experiment = (
        db.query(Experiment)
        .options(joinedload(Experiment.data))
        .filter(
            Experiment.id == experiment_id,
            Experiment.user_id == current_user.id,
        )
        .first()
    )

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if experiment.data is None:
        raise HTTPException(
            status_code=400,
            detail="No experiment data uploaded. Upload aggregate data before running analysis.",
        )

    # Queue the task
    task = run_analysis_task.delay(
        run_id=str(run_req.id),
        experiment_id=str(experiment_id),
        method=run_req.method,
        n_a=experiment.data.n_a,
        conv_a=experiment.data.conv_a,
        n_b=experiment.data.n_b,
        conv_b=experiment.data.conv_b,
        n_sim=run_req.n_sim or 20000,
        seed=run_req.seed or 42
    )
    
    print(f"✅ Task queued with ID: {task.id}")  # Debug
    
    return RunResponse.from_orm(new_run)