from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.excuse_letter import ExcuseLetter
from app.models.event import Event
from app.models.user import StudentProfile, User
from app.models.attendance import AttendanceRecord
from app.schemas.excuse_letter import ExcuseLetterCreate, ExcuseLetterReview, ExcuseLetterResponse
from app.services.auth import get_current_user
from app.core.timezones import utc_now

router = APIRouter(prefix="/excuse-letters", tags=["Excuse Letters"])

@router.post("/events/{event_id}", response_model=ExcuseLetterResponse)
def submit_excuse_letter(
    event_id: int,
    payload: ExcuseLetterCreate,
    student_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify student exists
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Verify event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if letter already exists
    existing = db.query(ExcuseLetter).filter(
        ExcuseLetter.student_profile_id == student_id,
        ExcuseLetter.event_id == event_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Excuse letter already submitted for this event")

    letter = ExcuseLetter(
        student_profile_id=student_id,
        event_id=event_id,
        reason=payload.reason,
        attachment_url=payload.attachment_url,
        status="Pending"
    )
    db.add(letter)
    db.commit()
    db.refresh(letter)
    
    return ExcuseLetterResponse(
        id=letter.id,
        event_id=letter.event_id,
        eventName=event.name,
        studentName=f"{student.first_name} {student.last_name}",
        status=letter.status,
        reason=letter.reason,
        attachment_url=letter.attachment_url,
        submittedAt=letter.created_at
    )

@router.get("", response_model=List[ExcuseLetterResponse])
def get_excuse_letters(
    scope: str = Query(..., description="student or governance"),
    student_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ExcuseLetter).join(Event).join(StudentProfile)

    if scope == "student":
        if not student_id:
            raise HTTPException(status_code=400, detail="student_id required for student scope")
        query = query.filter(ExcuseLetter.student_profile_id == student_id)
    elif scope == "governance":
        # In a full implementation, we'd filter by unit_id and governance hierarchy.
        # For now, we return all letters if authorized as officer.
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid scope")

    letters = query.order_by(ExcuseLetter.created_at.desc()).all()
    
    result = []
    for l in letters:
        result.append(ExcuseLetterResponse(
            id=l.id,
            event_id=l.event_id,
            eventName=l.event.name,
            studentName=f"{l.student.first_name} {l.student.last_name}",
            course=l.student.program.code if l.student.program else None,
            status=l.status,
            reason=l.reason,
            attachment_url=l.attachment_url,
            reviewerRemarks=l.reviewer_remarks,
            submittedAt=l.created_at
        ))
    return result

@router.post("/{letter_id}/review", response_model=ExcuseLetterResponse)
def review_excuse_letter(
    letter_id: int,
    payload: ExcuseLetterReview,
    reviewer_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    letter = db.query(ExcuseLetter).filter(ExcuseLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(status_code=404, detail="Excuse letter not found")

    if payload.status not in ["Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    letter.status = payload.status
    letter.reviewer_id = reviewer_id
    letter.reviewer_remarks = payload.remarks
    letter.updated_at = utc_now()

    # If approved, update attendance record to excused
    if payload.status == "Approved":
        attendance = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_profile_id == letter.student_profile_id,
            AttendanceRecord.event_id == letter.event_id
        ).first()
        
        if attendance:
            attendance.status_code = "excused"
        else:
            # Create an excused record if none exists
            new_record = AttendanceRecord(
                student_profile_id=letter.student_profile_id,
                event_id=letter.event_id,
                status_code="excused",
                method_code="manual", # Assuming manual override method
                notes=f"Excused via approved letter ID {letter.id}"
            )
            db.add(new_record)

    db.commit()
    db.refresh(letter)

    return ExcuseLetterResponse(
        id=letter.id,
        event_id=letter.event_id,
        eventName=letter.event.name,
        studentName=f"{letter.student.first_name} {letter.student.last_name}",
        course=letter.student.program.code if letter.student.program else None,
        status=letter.status,
        reason=letter.reason,
        attachment_url=letter.attachment_url,
        reviewerRemarks=letter.reviewer_remarks,
        submittedAt=letter.created_at
    )
