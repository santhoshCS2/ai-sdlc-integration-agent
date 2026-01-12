from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class APIKeyBase(BaseModel):
    label: str
    expires_at: Optional[datetime] = None

class APIKeyCreate(APIKeyBase):
    pass

class APIKey(APIKeyBase):
    id: int
    key_preview: str
    owner_id: int
    is_revoked: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SystemLogBase(BaseModel):
    event_type: str
    description: str
    severity: str

class SystemLog(SystemLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PerformanceMetricBase(BaseModel):
    agent_id: int
    latency_ms: float
    request_count: int = 1
    error_rate: float = 0.0

class PerformanceMetric(PerformanceMetricBase):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True
