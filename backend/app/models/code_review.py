from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base

class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    original_repo_url = Column(String)
    updated_repo_url = Column(String)
    scan_report = Column(Text)
    changes_summary = Column(Text)
    diff_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
