from celery import shared_task
from app.core.celery_app import celery_app
from app.services.stats import z_test_two_proportions, permutation_test
from app.core.db import SessionLocal
from app.models.run import Run, RunResult
from sqlalchemy import update
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.db import SessionLocal
from app.models.run import Run, RunResult
from app.services.stats import z_test_two_proportions, permutation_test, generate_summary

@celery_app.task(bind=True)
def run_analysis_task(
    self,
    run_id: str, 
    experiment_id: str, 
    method: str, 
    n_a: int, 
    conv_a: int, 
    n_b: int, 
    conv_b: int, 
    n_sim: int = 20000, 
    seed: int = 42
):
    """Background task: run statistical analysis."""
    
    db = SessionLocal()
    
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            raise ValueError(f"Run {run_id} not found")
            
        run.status = "running"
        run.started_at = datetime.utcnow()
        db.commit()
        
        if method == "ztest":
            results = z_test_two_proportions(n_a, conv_a, n_b, conv_b)
        elif method == "permutation":
            results = permutation_test(
                n_a=n_a,
                conv_a=conv_a,
                n_b=n_b,
                conv_b=conv_b,
                n_sim=n_sim,
                seed=seed
            )
        else:
            raise ValueError(f"Unknown method: {method}")
        
        run_result = RunResult(
            run_id=run_id,
            observed_lift=results['observed_lift'],
            p_value=results['p_value'],
            z_statistic=results.get('z_statistic'),
            ci_low=results.get('ci_low'),
            ci_high=results.get('ci_high'),
            significant=results.get('significant', False),
            summary_json=results.get('summary', {})
        )
        
        db.add(run_result)
        
        run.status = "success"
        run.finished_at = datetime.utcnow()
        run.progress = 1.0
        
        db.commit()
        
        return {
            "status": "success",
            "run_id": run_id,
            "results": results
        }
    
    except Exception as e:
        # Rollback and mark as failed
        db.rollback()
        run = db.query(Run).filter(Run.id == run_id).first()
        if run:
            run.status = "failed"
            run.error_message = str(e)
            run.finished_at = datetime.utcnow()
            db.commit()
        raise
    
    finally:
        db.close()