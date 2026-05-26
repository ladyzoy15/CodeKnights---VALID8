from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ExcuseLetterCreate(BaseModel):
    reason: str
    attachment_url: Optional[str] = None

class ExcuseLetterReview(BaseModel):
    status: str  # Approved, Rejected
    remarks: Optional[str] = None

class ExcuseLetterResponse(BaseModel):
    id: int
    event_id: int
    eventName: str
    studentName: str
    course: Optional[str] = None
    yearLevel: Optional[str] = None
    status: str
    reason: str
    attachment_url: Optional[str] = None
    reviewerRemarks: Optional[str] = None
    submittedAt: datetime

    class Config:
        from_attributes = True
