from sqlalchemy.orm import Session
from app.models.system import SystemLog, PerformanceMetric
from datetime import datetime

def create_log(db: Session, event_type: str, description: str, severity: str):
    db_log = SystemLog(event_type=event_type, description=description, severity=severity)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SystemLog).order_by(SystemLog.created_at.desc()).offset(skip).limit(limit).all()

def record_metric(db: Session, agent_id: int, latency_ms: float, error: bool = False):
    metric = PerformanceMetric(
        agent_id=agent_id,
        latency_ms=latency_ms,
        error_rate=1.0 if error else 0.0
    )
    db.add(metric)
    db.commit()
    return metric
