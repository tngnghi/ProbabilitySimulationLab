from datetime import datetime
from typing import Optional, Literal, Any, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field, model_validator
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
    model_config = ConfigDict(from_attributes=True)

    conversion_rate_a: float
    conversion_rate_b: float

    absolute_lift: float
    relative_lift: Optional[float] = None

    p_value: float
    z_statistic: Optional[float] = None

    absolute_lift_ci_low: Optional[float] = None
    absolute_lift_ci_high: Optional[float] = None

    significant: bool
    summary_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    experiment_id: UUID
    method: str
    n_sim: Optional[int] = None
    seed: Optional[int] = None
    status: str
    progress: float
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    results: Optional[RunResultResponse] = None