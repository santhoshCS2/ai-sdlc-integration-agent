from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChangeItem(BaseModel):
    file: str
    issues_fixed: List[str]
    diff: str

class ReviewResponse(BaseModel):
    id: int
    original_repo_url: str
    updated_repo_url: str
    change_report: List[ChangeItem]
    changes_summary: str
    created_at: datetime

class ReviewRequest(BaseModel):
    repo_url: str
    scan_report: Optional[str] = None
