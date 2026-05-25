"""Use: Pydantic schemas for the Excuse Letter feature.
Where to use: Used by the excuse_letters router for request validation and response serialization.
Role: Schema layer. Defines data shapes moving in and out of the API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class ExcuseLetterSubmitRequest(BaseModel):
    reason: str
    attachment_path: Optional[str] = None

    @field_validator("reason")
    @classmethod
    def reason_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Reason for absence is required.")
        return v.strip()


class ExcuseLetterReviewRequest(BaseModel):
    remarks: Optional[str] = None


# ── Nested sub-schemas ────────────────────────────────────────────────────────

class ExcuseLetterStudentInfo(BaseModel):
    user_id: int
    student_number: str
    full_name: str
    year_level: Optional[int]
    course: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True


class ExcuseLetterEventInfo(BaseModel):
    id: int
    name: str
    start_at: datetime
    status: str

    class Config:
        from_attributes = True


class ExcuseLetterReviewerInfo(BaseModel):
    user_id: int
    full_name: str

    class Config:
        from_attributes = True


# ── Primary response schema ───────────────────────────────────────────────────

class ExcuseLetterResponse(BaseModel):
    id: int
    school_id: int
    event_id: int
    student_profile_id: int
    reason: str
    attachment_path: Optional[str]
    status: str
    reviewer_remarks: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Enriched nested objects (populated by service)
    student: Optional[ExcuseLetterStudentInfo] = None
    event: Optional[ExcuseLetterEventInfo] = None
    reviewer: Optional[ExcuseLetterReviewerInfo] = None

    class Config:
        from_attributes = True


# ── Lightweight status-only response (for event card badge) ──────────────────

class ExcuseLetterStatusResponse(BaseModel):
    letter_id: Optional[int] = None
    status: Optional[str] = None  # None means no letter submitted yet
    reviewer_remarks: Optional[str] = None
    reviewed_at: Optional[datetime] = None


# ── Officer dashboard cross-event summary ────────────────────────────────────

class ExcuseLetterDashboardResponse(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int
