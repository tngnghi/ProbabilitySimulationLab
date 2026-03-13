from datetime import datetime
import enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field
from uuid import UUID


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
    description: str |None = None
    alpha: float
    two_sided: bool
    metric: str
    created_at: datetime
    updated_at: datetime
    data: Optional[dict] = None
    warnings: Optional[list[str]] = None

    model_config = ConfigDict(from_attributes =True, arbitrary_types_allowed =True)

class ExperimentDataCreate(BaseModel):
    n_a: int = Field(..., gt=0)
    conv_a: int = Field(..., ge=0)
    n_b: int = Field(..., gt=0)
    conv_b: int = Field(..., ge=0)

    @field_validator("n_a", "n_b")
    def check_positive(cls,value):
        if value <= 0:
            raise ValueError("must be > 0")
        return value
    
    @field_validator('conv_a')
    def check_conv_a(cls, v, info):
        if v < 0:
            raise ValueError('must be >= 0')
        if v > info.data.get('n_a', 0):
            raise ValueError('conv_a cannot exceed n_a')
        return v
    
    @field_validator('conv_b')
    def check_conv_b(cls, v, info):
        if v < 0:
            raise ValueError('must be >= 0')
        if v > info.data.get('n_b', 0):
            raise ValueError('conv_b cannot exceed n_b')
        return v
    
class ExperimentDataResponse(BaseModel):
    n_a: int
    conv_a: int
    n_b: int
    conv_b: int
    data_source: str = Field(enum)
    updated_at: datetime = Field(default_factory=datetime.now)
    warnings: Optional[list[str]] = None
    
    model_config = ConfigDict(from_attributes = True)

class ExperimentDataUpdate(BaseModel):
    n_a: Optional[int] = None
    conv_a: Optional[int] = None
    n_b: Optional[int] = None
    conv_b: Optional[int] = None