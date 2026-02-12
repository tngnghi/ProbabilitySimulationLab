from ast import List
import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, PaginatedExperimentResponse
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.core import db
from app.schemas.experiment import ExperimentDataResponse, ExperimentResponse, ExperimentUpdate, ExperimentCreateRequest
from app.models.experiment import Experiment, ExperimentData
from sqlalchemy.orm import Session, joinedload
from uuid import uuid4, UUID

router = APIRouter(prefix="/experiments", tags=["experiments"])

@router.post("", status_code=201, response_model=ExperimentResponse)
async def create_experiment(experiment_data: ExperimentCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_experiment = Experiment(
        id=uuid4(),
        user_id=current_user.id,
        name=experiment_data.name,
        description=experiment_data.description,
        alpha=experiment_data.alpha,
        two_sided=experiment_data.two_sided,
        metric=experiment_data.metric,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    existing_name = db.query(Experiment).filter(Experiment.user_id == current_user.id, Experiment.name == experiment_data.name).first()

    if existing_name:
        raise HTTPException(status_code=400, detail="Experiment name already exists for this user")
    db.add(new_experiment)
    db.commit()
    db.refresh(new_experiment)
    return new_experiment


@router.get("", response_model=List[ExperimentResponse])
async def list_experiments(current_user: User = Depends(get_current_user), skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    experiments = db.query(Experiment).filter(Experiment.user_id == current_user.id).options(joinedload(Experiment.data)).order_by(Experiment.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(Experiment).filter(Experiment.user_id == current_user.id).count()
    items = [ExperimentResponse.from_orm(exp) for exp in experiments]
    return PaginatedExperimentResponse(total=total, items=items, skip=skip, limit=limit)


@router.get("/{experiment_id}", response_model=ExperimentResponse, status_code=200)
async def get_experiment(experiment_id: UUID, current_user: User = Depends(get_current_user)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).options(joinedload(Experiment.data)).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if experiment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this experiment")
    data = db.query(ExperimentData).filter(ExperimentData.experiment_id == experiment.id).all()
    response = ExperimentResponse(
        id=experiment.id,
        user_id=experiment.user_id,
        name=experiment.name,
        description=experiment.description,
        alpha=experiment.alpha,
        two_sided=experiment.two_sided,
        metric=experiment.metric,
        created_at=experiment.created_at,
        updated_at=experiment.updated_at,
        data=ExperimentDataResponse(data=data)
    )
    return response


@router.patch("/{experiment_id}", response_model=ExperimentResponse, status_code=200)
async def update_experiment(experiment_id: UUID, update_data:ExperimentUpdate, current_user: User = Depends(get_current_user)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if experiment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this experiment")
    
    # Check for name conflict
    existing_name = db.query(Experiment).filter(Experiment.user_id == current_user.id, Experiment.id != experiment_id).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="Experiment name already exists for this user")
    
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

    experiment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(experiment)
    data = db.query(ExperimentData).filter(ExperimentData.experiment_id == experiment.id).all()
    experiment_response = ExperimentResponse(
        id=experiment.id,
        user_id=experiment.user_id,
        name=experiment.name,
        description=experiment.description,
        alpha=experiment.alpha,
        two_sided=experiment.two_sided,
        metric=experiment.metric,
        created_at=experiment.created_at,
        updated_at=experiment.updated_at,
        data=ExperimentDataResponse(data=data)
    )
    return experiment_response


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(experiment_id: UUID, current_user: User = Depends(get_current_user)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if experiment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this experiment")
    db.delete(experiment)
    db.commit()
    response = {"message": "Experiment deleted successfully"}
    return response

@router.post("/{experiment_id}/data/aggregate", response_model=ExperimentDataResponse, status_code=200)
async def update_experiment_data(experiment_id: UUID, data: ExperimentUpdate, current_user: User = Depends(get_current_user)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id, Experiment.user_id == current_user.id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if experiment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this experiment's data")
    
    existing_data = db.query(ExperimentData).filter(ExperimentData.experiment_id == experiment_id).first()
    
    if existing_data.con_a > existing_data.n_a or existing_data.conv_b > existing_data.n_b:
        raise HTTPException(status_code=422, detail="Conv_A cannot be greater than N_A and Conv_B cannot be greater than N_B")
    if existing_data:
        if data.n_a is not None:
            existing_data.n_a = data.n_a
        if data.conv_a is not None:
            existing_data.conv_a = data.conv_a
        if data.n_b is not None:
            existing_data.n_b = data.n_b
        if data.conv_b is not None:
            existing_data.conv_b = data.conv_b
        existing_data.updated_at = datetime.utcnow()
    else:
        new_data = ExperimentData(
            experiment_id=experiment_id,
            n_a=data.n_a,
            conv_a=data.conv_a,
            n_b=data.n_b,
            conv_b=data.conv_b,
            data_source="aggregate",
            updated_at=datetime.utcnow()
        )
        db.add(new_data)
    
    db.commit()
    updated_data = db.query(ExperimentData).filter(ExperimentData.experiment_id == experiment_id).first()
    return updated_data