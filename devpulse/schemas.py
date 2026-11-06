from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class TargetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    url: HttpUrl
    timeout_seconds: float = Field(default=5, gt=0, le=30)
    latency_threshold_ms: float = Field(default=800, gt=0)

class TargetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    url: str
    timeout_seconds: float
    latency_threshold_ms: float
    created_at: datetime

class CheckResponse(BaseModel):
    id: int
    target_id: int
    is_up: bool
    status_code: int | None
    latency_ms: float
    error: str | None
    checked_at: datetime

class IncidentResponse(BaseModel):
    id: int
    target_id: int
    kind: str
    message: str
    active: bool
    created_at: datetime
    resolved_at: datetime | None
