from scipy.stats import norm
import math

def generate_summary(observed_lift, p_value, significant, alpha=0.05) -> str:
    """
    Generate plain-English summary of results.
    
    Input: results dict from z_test
    Output: string like "Variant B significantly outperforms A (p=0.032, lift=12.5%)"
    """
    
    if significant:
        if observed_lift > 0:
            return f"Variant B significantly outperforms A (p={p_value:.3f}, lift={observed_lift*100:.1f}%)"
        else:
            return f"Variant A significantly outperforms B (p={p_value:.3f}, lift={abs(observed_lift)*100:.1f}%)"
    else:
        return f"No significant difference detected (p={p_value:.3f}, lift={observed_lift*100:.1f}%)"

def z_test_two_proportions(n_a: int, conv_a: int, n_b: int, conv_b: int, two_sided: bool = True):
    if n_a <= 0:
        raise ValueError("n_a must be > 0")
    if n_b <= 0:
        raise ValueError("n_b must be > 0")
    if conv_a > n_a or conv_b > n_b:
        raise ValueError("Conversions cannot exceed samples")
    
    alpha = 0.5  # pseudocount
            
    conv_a_smooth = conv_a + alpha
    n_a_smooth = n_a + 2 * alpha
    
    conv_b_smooth = conv_b + alpha
    n_b_smooth = n_b + 2 * alpha
    
    p_hat_a = conv_a_smooth / n_a_smooth
    p_hat_b = conv_b_smooth / n_b_smooth
    
    observed_lift = (p_hat_b - p_hat_a) / p_hat_a
    p_hat_pooled = (conv_a + conv_b) / (n_a + n_b)
    se = math.sqrt(p_hat_pooled * (1 - p_hat_pooled) * (1/n_a + 1/n_b))
    
    if se == 0:
        if se == 0:
            raise ValueError(
            "Cannot compute z-test: no variation in data. "
            "Both variants have identical conversion rates (0% or 100%). "
            "Need at least some variation to test."
            )
    
    z = (p_hat_b - p_hat_a) / se
    
    if two_sided:
        p_value = 2 * (1 - norm.cdf(abs(z)))
    else: p_value = 1 - norm.cdf(abs(z))
    ci_low = p_hat_b - 1.96 * math.sqrt(p_hat_b * (1 - p_hat_b) / n_b)
    ci_high = p_hat_b + 1.96 * math.sqrt(p_hat_b * (1 - p_hat_b) / n_b)

    
    if p_value < 0.05:
        significant = True
    
    return {
        "observed_lift": observed_lift,
        "p_hat_a": p_hat_a,
        "p_hat_b": p_hat_b,
        "z_statistic": z,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "significant": significant
        }

"""I see you've shared your GitHub repository link, but it’s not yet available. Based on the errors you've been encountering, I’ll provide **exact code fixes** you can apply to your existing files.

## Root cause summary

1. **NumPy types** (`np.float64`, `np.bool_`) are not JSON serializable → SQLAlchemy fails when inserting into a `JSON` column (`summary_json`).  
2. **Confidence intervals** are computed for `p_hat_b` alone, not for the lift → they remain `None` (or wrong).  
3. **Session rollback** missing after an exception → `PendingRollbackError` on subsequent commits.  
4. Generic `{"detail":"Analysis failed"}` hides the real error.

## Fix 1 – Convert NumPy types to Python natives

Modify your `z_test_two_proportions` function to return plain Python types.

```python
import math
from scipy.stats import norm

def z_test_two_proportions(n_a: int, conv_a: int, n_b: int, conv_b: int, two_sided: bool = True):
    # ... (your validation and smoothing logic) ...

    # Convert everything to Python float/bool before returning
    return {
        "observed_lift": float(observed_lift),
        "p_value": float(p_value),
        "z_statistic": float(z),
        "ci_low": float(ci_low) if ci_low is not None else None,
        "ci_high": float(ci_high) if ci_high is not None else None,
        "significant": bool(significant),
        "summary": str(summary)   # ensure string
    }
```

## Fix 2 – Compute confidence interval for the **absolute difference**

Replace your current CI lines with:

```python
# Standard error of the difference (unpooled)
se_diff = math.sqrt(p_hat_a*(1-p_hat_a)/n_a + p_hat_b*(1-p_hat_b)/n_b)
z_crit = norm.ppf(0.975)   # 1.96
ci_low = (p_hat_b - p_hat_a) - z_crit * se_diff
ci_high = (p_hat_b - p_hat_a) + z_crit * se_diff
```

This gives you the 95% confidence interval for the **absolute lift** (`p_hat_b - p_hat_a`). If you want relative lift CI, you'll need a different method (e.g., delta method), but the above is standard for two-proportion z‑tests.

## Fix 3 – In your endpoint (`uploads_run`), clean the result and handle rollback

```python
@router.post("/experiments/{experiment_id}/runs")
def uploads_run(experiment_id: UUID, ... , db: Session = Depends(get_db)):
    try:
        # ... get experiment, validate, compute stats ...
        result = z_test_two_proportions(n_a, conv_a, n_b, conv_b)

        # Ensure no NumPy types (redundant but safe)
        result = {k: (float(v) if isinstance(v, (np.floating, np.integer)) else
                      bool(v) if isinstance(v, np.bool_) else v)
                  for k, v in result.items()}

        run_result = RunResult(
            run_id=uuid4(),
            experiment_id=experiment_id,
            method="ztest",
            status="success",
            created_at=datetime.utcnow(),
            started_at=start_time,
            finished_at=datetime.utcnow(),
            results=result,          # or summary_json, depending on your model
            # ... other fields ...
        )
        db.add(run_result)
        db.commit()
        db.refresh(run_result)
        return run_result

    except Exception as e:
        db.rollback()
        # Log the full error for debugging
        print(f"Error in run creation: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))   # or a generic message
```

## Fix 4 – Update your SQLAlchemy model (if using `JSON` column)

Make sure the column that stores the results is defined with `JSON` (or `JSONB` for PostgreSQL). If you store the whole result dict in `summary_json`, ensure it's a `JSON` column.

```python
from sqlalchemy import JSON

class RunResult(Base):
    # ...
    summary_json = Column(JSON, nullable=True)   # or results = Column(JSON)
```

## Fix 5 – Use Pydantic response model with optional fields

To avoid `ResponseValidationError`, make `ci_low` and `ci_high` optional in your response schema.

```python
from typing import Optional

class RunResultResponse(BaseModel):
    id: UUID
    experiment_id: UUID
    method: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    results: dict   # or a nested model
    # or specifically:
    # ci_low: Optional[float] = None
    # ci_high: Optional[float] = None
```

## Final check

After applying all fixes:

1. Restart the server.
2. Test with a valid experiment and sample data (e.g., `n_a=100, conv_a=50, n_b=100, conv_b=75`).
3. You should get a `201` response with numeric `ci_low`/`ci_high` and no `null`s.

If you still see `{"detail":"Analysis failed"}`, check your server console for the **full traceback** – the real error is being swallowed by a generic `except`. Remove any bare `except:` and let the error propagate, or log it properly.

For further help, please make your repository public or share the exact code of `experiments.py` and `models.py`. The fixes above, however, should resolve all issues you've shown so far."""