import datetime
import enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import UUID


class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default="", max_length=500)
    alpha: Optional[float] = Field(0.05)  
    two_sided: Optional[bool] = True
    metric: Optional[str] = "conversion"

    @field_validator("alpha")
    @classmethod
    def validate_alpha(cls, value):
        if not 0 <= value <= 1:
            raise ValueError("Alpha must be between 0 and 1")
        return value
    
    @field_validator("metric")
    @classmethod
    def validate_metric(cls, value):
        allowed_metrics = {"conversion", "clicks", "order_value"}
        if value not in allowed_metrics:
            raise ValueError(f"Metric must be one of {allowed_metrics}")
        return value

class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    alpha: Optional[float] = None
    two_sided: Optional[bool] = None
    metric: Optional[str] = None

class ExperimentResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str
    alpha: float
    two_sided: bool
    metric: str
    created_at: datetime
    updated_at: datetime
    data: Optional[dict] = None

    class Config:
        from_attributes = True

class ExperimentDataCreate(BaseModel):
    n_a: int = Field(..., min_length=1, gt=0)
    conv_a: int = Field(...,min_length=1, ge=0)
    n_b: int = Field(..., min_length=1, gt=0)
    conv_b: int = Field(..., min_length=1, ge=0)

class ExperimentDataResponse(BaseModel):
    n_a: int
    conv_a: int
    n_b: int
    conv_b: int
    data_source: str = Field(enum)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def conv_rate_a(self) -> float:
        return self.conv_a / self.n_a if self.n_a > 0 else 0.0
    
    @property
    def conv_rate_b(self) -> float:
        return self.conv_b / self.n_b if self.n_b > 0 else 0.0
    
    @property
    def observed_lift(self) -> float:
        return (self.conv_rate_b - self.conv_rate_a) / self.conv_rate_a if self.conv_rate_a > 0 else 0.0
    
    class Config:
        from_attributes = True