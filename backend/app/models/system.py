from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String)
    key_preview = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=True)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", backref="api_keys")

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    description = Column(Text)
    severity = Column(String)  # INFO, WARNING, ERROR, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    latency_ms = Column(Float)
    request_count = Column(Integer, default=1)
    error_rate = Column(Float, default=0.0)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", backref="metrics")
