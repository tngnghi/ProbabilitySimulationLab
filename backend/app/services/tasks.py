from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.db import SessionLocal
from app.models.run import Run, RunResult
from app.services.stats import z_test_two_proportions, permutation_test, generate_summary

@shared_task(bind=True)
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
    """
    Background task: run statistical analysis.
    Called asynchronously from POST /experiments/{id}/runs
    """
    
    db = SessionLocal()
    
    try:
        # 1. Update Run status to "running"
        run = db.query(Run).filter(Run.id == run_id).first()
        run.status = "running"
        run.started_at = datetime.utcnow()
        db.commit()
        
        # 2. Run analysis based on method
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
        
        # 3. Generate summary
        summary = generate_summary(
            observed_lift=results['observed_lift'],
            p_value=results['p_value'],
            significant=results.get('significant', False)
        )
        
        # 4. Create RunResult
        run_result = RunResult(
            run_id=run_id,
            observed_lift=results['observed_lift'],
            p_value=results['p_value'],
            z_statistic=results.get('z_statistic'),
            ci_low=results.get('ci_low'),
            ci_high=results.get('ci_high'),
            significant=str(results.get('significant', False)),
            summary_json=f'{{"summary": "{summary}"}}'
        )
        
        db.add(run_result)
        
        # 5. Update Run status to "success"
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
        # Error handling
        run = db.query(Run).filter(Run.id == run_id).first()
        run.status = "failed"
        run.error_message = str(e)
        run.finished_at = datetime.utcnow()
        db.commit()
        
        raise
    
    finally:
        db.close()