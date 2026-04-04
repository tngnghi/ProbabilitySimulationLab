from datetime import datetime
from typing import Optional, Literal, Any
from pydantic import BaseModel, Field, field_validator, computed_field, model_validator
from uuid import UUID

class RunCreate(BaseModel):
    method: Literal["ztest", "permutation"]
    n_sim:  Optional[int] = Field(default = 20000)
    seed: Optional[int] = Field(default = 42)
    compute_power: Optional[bool] = Field(default = False)

    @model_validator(mode='after')
    def validate_conditional_logic(self) -> 'RunCreate':
        if self.method == "permutation":
            if self.n_sim is not None and not (100 < self.n_sim < 1000000):
                raise ValueError("n_sim must be > 100 and < 1000000 for permutation")
            if self.seed is not None and self.seed < 0:
                raise ValueError("seed must be >= 0")
        return self
    
class RunResultResponse(BaseModel):
    observed_lift: float
    p_value: float
    z_statistic: Optional[float] = None
    ci_low: float
    ci_high: float
    significant: bool
    summary_json: Optional[dict[str, Any]] = Field(None, exclude=True)

    @computed_field
    @property
    def summary(self) -> str:
        """Dynamically extracts the summary text from the JSON blob."""
        if self.summary_json and "summary" in self.summary_json:
            return self.summary_json["summary"]
        return "No summary available."

class RunResponse(BaseModel):
    run_id: UUID
    experiment_id: UUID
    method: str
    status: Literal["queued", "running", "success", "failed"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    progress: Optional[float] = Field(default = None, ge = 0.0, le = 1.0)
    error_message: Optional[str]
    results: Optional[RunResultResponse] = None

    @model_validator(mode='after')
    def validate_run_status(self) -> 'RunResponse':
        if self.status == "success" and self.results is None:
            raise ValueError("results are required when status is 'success'")
        if self.status != "success" and self.results is not None:
            raise ValueError("results must be null unless status is 'success'")
        
        if self.status == "failed" and not self.error_message:
            raise ValueError("error_message is required when status is 'failed'")
            
        return self
