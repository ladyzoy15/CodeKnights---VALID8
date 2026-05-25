"""Use: Handles Excuse Letter system API endpoints.
Where to use: Register in main.py for student submission and officer review of excuse letters.
Role: Router layer. Handles access control, parameter validation, and endpoint definitions.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user_with_roles
from app.models.user import User
from app.schemas.excuse_letter import (
    ExcuseLetterDashboardResponse,
    ExcuseLetterResponse,
    ExcuseLetterReviewRequest,
    ExcuseLetterStatusResponse,
    ExcuseLetterSubmitRequest,
)
from app.services import excuse_letter_service

router = APIRouter(prefix="/excuse-letters", tags=["excuse-letters"])


@router.post("/events/{event_id}/submit", response_model=ExcuseLetterResponse, status_code=status.HTTP_201_CREATED)
def submit_excuse_letter(
    event_id: int,
    payload: ExcuseLetterSubmitRequest,
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """Submit an excuse letter for an upcoming event (Student only)."""
    return excuse_letter_service.submit_excuse_letter(
        db,
        current_user=current_user,
        event_id=event_id,
        payload=payload,
    )


@router.get("/events/{event_id}/status", response_model=ExcuseLetterStatusResponse)
def get_excuse_letter_status_for_event(
    event_id: int,
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """Retrieve this student's excuse letter status for a specific event."""
    return excuse_letter_service.get_excuse_letter_status_for_event(
        db,
        current_user=current_user,
        event_id=event_id,
    )


@router.get("/students/me", response_model=list[ExcuseLetterResponse])
def get_my_excuse_letters(
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """Retrieve all excuse letters submitted by the current student."""
    return excuse_letter_service.get_my_excuse_letters(
        db,
        current_user=current_user,
    )


@router.get("/events/{event_id}/submissions", response_model=list[ExcuseLetterResponse])
def list_excuse_letters_for_event(
    event_id: int,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=250),
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """List excuse letters submitted for a specific event (Officer review, scoped)."""
    return excuse_letter_service.list_excuse_letters_for_event(
        db,
        current_user=current_user,
        event_id=event_id,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )


@router.get("/submissions", response_model=list[ExcuseLetterResponse])
def list_all_excuse_letters(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=250),
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """List all excuse letters across events (Officer cross-event dashboard view, scoped)."""
    return excuse_letter_service.list_all_excuse_letters(
        db,
        current_user=current_user,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )


@router.post("/{letter_id}/approve", response_model=ExcuseLetterResponse)
def approve_excuse_letter(
    letter_id: int,
    payload: ExcuseLetterReviewRequest,
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """Approve a pending excuse letter (Officer only, permission & scope checked)."""
    return excuse_letter_service.approve_excuse_letter(
        db,
        current_user=current_user,
        letter_id=letter_id,
        payload=payload,
    )


@router.post("/{letter_id}/reject", response_model=ExcuseLetterResponse)
def reject_excuse_letter(
    letter_id: int,
    payload: ExcuseLetterReviewRequest,
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """Reject a pending excuse letter (Officer only, permission & scope checked)."""
    return excuse_letter_service.reject_excuse_letter(
        db,
        current_user=current_user,
        letter_id=letter_id,
        payload=payload,
    )


@router.get("/dashboard", response_model=ExcuseLetterDashboardResponse)
def get_excuse_letter_dashboard(
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """Retrieve quick metrics for the governance officer dashboard."""
    return excuse_letter_service.get_excuse_letter_dashboard(
        db,
        current_user=current_user,
    )


@router.post("/upload-attachment", response_model=dict)
def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_with_roles),
    db: Session = Depends(get_db),
):
    """Upload a supporting attachment for an excuse letter."""
    file_bytes = file.file.read()
    path = excuse_letter_service.upload_excuse_letter_attachment(
        db,
        current_user=current_user,
        filename=file.filename or "attachment",
        file_bytes=file_bytes,
    )
    return {"attachment_path": path}
