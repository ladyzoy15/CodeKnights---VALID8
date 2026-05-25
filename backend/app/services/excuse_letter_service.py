"""Use: Contains all business logic for the Excuse Letter feature.
Where to use: Called from the excuse_letters router. Never called directly from models.
Role: Service layer. Enforces submission rules, governance scope, notifications, and audit logging.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.timezones import utc_now
from app.models.event import Event, EventStatus
from app.models.excuse_letter import ExcuseLetter, ExcuseLetterStatus
from app.models.governance_hierarchy import (
    GovernanceMember,
    GovernanceMemberPermission,
    GovernancePermission,
    GovernanceUnit,
    GovernanceUnitPermission,
    PermissionCode,
)
from app.models.user import StudentProfile, User
from app.schemas.excuse_letter import (
    ExcuseLetterDashboardResponse,
    ExcuseLetterEventInfo,
    ExcuseLetterResponse,
    ExcuseLetterReviewerInfo,
    ExcuseLetterStatusResponse,
    ExcuseLetterStudentInfo,
    ExcuseLetterSubmitRequest,
    ExcuseLetterReviewRequest,
)
from app.services.notification_center_service import send_notification_to_user


# ── Governance scope helpers ──────────────────────────────────────────────────

_UNIT_TYPE_RANK = {"SSG": 3, "SG": 2, "ORG": 1}


def _get_user_governance_unit_types(db: Session, *, current_user: User) -> list[str]:
    """Return all unit_type values the current user is an active member of."""
    rows = (
        db.query(GovernanceUnit.unit_type)
        .join(GovernanceMember, GovernanceMember.governance_unit_id == GovernanceUnit.id)
        .filter(
            GovernanceMember.user_id == current_user.id,
            GovernanceMember.is_active.is_(True),
            GovernanceUnit.is_active.is_(True),
        )
        .distinct()
        .all()
    )
    return [row[0] for row in rows]


def _event_creator_unit_type(db: Session, *, event: Event) -> Optional[str]:
    """Return the governance unit_type of the user who created the event, if any."""
    if event.created_by_user_id is None:
        return None
    row = (
        db.query(GovernanceUnit.unit_type)
        .join(GovernanceMember, GovernanceMember.governance_unit_id == GovernanceUnit.id)
        .filter(
            GovernanceMember.user_id == event.created_by_user_id,
            GovernanceMember.is_active.is_(True),
            GovernanceUnit.is_active.is_(True),
        )
        .first()
    )
    return row[0] if row else None


def _officer_can_review_event(db: Session, *, current_user: User, event: Event) -> bool:
    """
    Scope rule from spec:
      SSG created → SSG, SG, ORG can review
      SG  created → SG, ORG can review
      ORG created → ORG only
    Campus admin/admin always can review.
    """
    from app.core.security import has_any_role
    if has_any_role(current_user, ["admin", "campus_admin"]):
        return True

    officer_types = _get_user_governance_unit_types(db, current_user=current_user)
    if not officer_types:
        return False

    event_creator_type = _event_creator_unit_type(db, event=event)
    if event_creator_type is None:
        # Event not owned by any governance unit — SSG members can review by default
        return "SSG" in officer_types

    creator_rank = _UNIT_TYPE_RANK.get(event_creator_type, 0)
    # Officer can review if their highest rank >= creator rank
    officer_max_rank = max(_UNIT_TYPE_RANK.get(t, 0) for t in officer_types)
    return officer_max_rank >= creator_rank


def _officer_has_review_permission(db: Session, *, current_user: User) -> bool:
    """Check if officer has the explicit review_excuse_letter permission assigned."""
    from app.core.security import has_any_role
    if has_any_role(current_user, ["admin", "campus_admin"]):
        return True

    permission_code_value = PermissionCode.REVIEW_EXCUSE_LETTER.value

    # Check member-level permission
    member_has = (
        db.query(GovernanceMemberPermission)
        .join(GovernanceMember, GovernanceMember.id == GovernanceMemberPermission.governance_member_id)
        .join(GovernancePermission, GovernancePermission.id == GovernanceMemberPermission.permission_id)
        .filter(
            GovernanceMember.user_id == current_user.id,
            GovernanceMember.is_active.is_(True),
            GovernancePermission.permission_code == permission_code_value,
        )
        .first()
    )
    if member_has:
        return True

    # Check unit-level permission
    unit_has = (
        db.query(GovernanceUnitPermission)
        .join(GovernancePermission, GovernancePermission.id == GovernanceUnitPermission.permission_id)
        .join(GovernanceUnit, GovernanceUnit.id == GovernanceUnitPermission.governance_unit_id)
        .join(GovernanceMember, GovernanceMember.governance_unit_id == GovernanceUnit.id)
        .filter(
            GovernanceMember.user_id == current_user.id,
            GovernanceMember.is_active.is_(True),
            GovernanceUnit.is_active.is_(True),
            GovernancePermission.permission_code == permission_code_value,
        )
        .first()
    )
    return bool(unit_has)


# ── Response builder ──────────────────────────────────────────────────────────

def _build_response(letter: ExcuseLetter) -> ExcuseLetterResponse:
    student_info = None
    if letter.student_profile:
        sp = letter.student_profile
        user = sp.user if hasattr(sp, "user") and sp.user else None
        full_name = " ".join(
            p for p in [
                getattr(user, "first_name", None),
                getattr(user, "last_name", None),
            ] if p
        ).strip() if user else ""
        program_name = None
        if hasattr(sp, "program") and sp.program:
            program_name = sp.program.name
        student_info = ExcuseLetterStudentInfo(
            user_id=user.id if user else 0,
            student_number=sp.student_id or "",
            full_name=full_name or (user.email if user else ""),
            year_level=sp.year_level,
            course=program_name,
            email=user.email if user else None,
        )

    event_info = None
    if letter.event:
        ev = letter.event
        event_info = ExcuseLetterEventInfo(
            id=ev.id,
            name=ev.name,
            start_at=ev.start_at,
            status=ev.status.value if hasattr(ev.status, "value") else str(ev.status),
        )

    reviewer_info = None
    if letter.reviewed_by_user:
        rv = letter.reviewed_by_user
        full_name = " ".join(
            p for p in [
                getattr(rv, "first_name", None),
                getattr(rv, "last_name", None),
            ] if p
        ).strip()
        reviewer_info = ExcuseLetterReviewerInfo(
            user_id=rv.id,
            full_name=full_name or rv.email,
        )

    return ExcuseLetterResponse(
        id=letter.id,
        school_id=letter.school_id,
        event_id=letter.event_id,
        student_profile_id=letter.student_profile_id,
        reason=letter.reason,
        attachment_path=letter.attachment_path,
        status=letter.status,
        reviewer_remarks=letter.reviewer_remarks,
        reviewed_at=letter.reviewed_at,
        created_at=letter.created_at,
        updated_at=letter.updated_at,
        student=student_info,
        event=event_info,
        reviewer=reviewer_info,
    )


def _load_letter_with_relations(db: Session, *, letter_id: int) -> ExcuseLetter:
    from app.models.user import StudentProfile as SP
    from app.models.program import Program
    letter = (
        db.query(ExcuseLetter)
        .options(
            joinedload(ExcuseLetter.event),
            joinedload(ExcuseLetter.student_profile).joinedload(SP.user),
            joinedload(ExcuseLetter.student_profile).joinedload(SP.program),
            joinedload(ExcuseLetter.reviewed_by_user),
        )
        .filter(ExcuseLetter.id == letter_id)
        .first()
    )
    if not letter:
        raise HTTPException(status_code=404, detail="Excuse letter not found.")
    return letter


# ── Notification helpers ──────────────────────────────────────────────────────

def _notify_student(db: Session, *, letter: ExcuseLetter, subject: str, message: str) -> None:
    if not letter.student_profile or not letter.student_profile.user:
        return
    student_user = letter.student_profile.user
    send_notification_to_user(
        db,
        user=student_user,
        school_id=letter.school_id,
        category="excuse_letter",
        subject=subject,
        message=message,
        deliver_in_app=True,
        metadata_json={"letter_id": letter.id, "event_id": letter.event_id},
    )


def _notify_officers_new_submission(db: Session, *, letter: ExcuseLetter) -> None:
    """Notify all active governance members with review_excuse_letter permission
    who are in scope for this event."""
    permission_code_value = PermissionCode.REVIEW_EXCUSE_LETTER.value

    # Collect user IDs with unit-level or member-level permission
    member_user_ids: set[int] = set()

    unit_rows = (
        db.query(GovernanceMember.user_id)
        .join(GovernanceUnit, GovernanceUnit.id == GovernanceMember.governance_unit_id)
        .join(GovernanceUnitPermission, GovernanceUnitPermission.governance_unit_id == GovernanceUnit.id)
        .join(GovernancePermission, GovernancePermission.id == GovernanceUnitPermission.permission_id)
        .filter(
            GovernanceMember.is_active.is_(True),
            GovernanceUnit.is_active.is_(True),
            GovernanceUnit.school_id == letter.school_id,
            GovernancePermission.permission_code == permission_code_value,
        )
        .distinct()
        .all()
    )
    member_user_ids.update(row[0] for row in unit_rows)

    member_rows = (
        db.query(GovernanceMember.user_id)
        .join(GovernanceUnit, GovernanceUnit.id == GovernanceMember.governance_unit_id)
        .join(GovernanceMemberPermission, GovernanceMemberPermission.governance_member_id == GovernanceMember.id)
        .join(GovernancePermission, GovernancePermission.id == GovernanceMemberPermission.permission_id)
        .filter(
            GovernanceMember.is_active.is_(True),
            GovernanceUnit.is_active.is_(True),
            GovernanceUnit.school_id == letter.school_id,
            GovernancePermission.permission_code == permission_code_value,
        )
        .distinct()
        .all()
    )
    member_user_ids.update(row[0] for row in member_rows)

    if not member_user_ids:
        return

    event_name = letter.event.name if letter.event else f"Event #{letter.event_id}"
    officers = db.query(User).filter(User.id.in_(member_user_ids)).all()
    for officer in officers:
        subject = f"New Excuse Letter: {event_name}"
        message = (
            f"Hi {officer.first_name or 'Officer'},\n\n"
            f"A student has submitted an excuse letter for the event: {event_name}.\n"
            "Please review it in the Excuse Letter management panel.\n\n"
            "NEXUS"
        )
        send_notification_to_user(
            db,
            user=officer,
            school_id=letter.school_id,
            category="excuse_letter",
            subject=subject,
            message=message,
            deliver_in_app=True,
            metadata_json={"letter_id": letter.id, "event_id": letter.event_id},
        )


# ── Public service functions ──────────────────────────────────────────────────

def submit_excuse_letter(
    db: Session,
    *,
    current_user: User,
    event_id: int,
    payload: ExcuseLetterSubmitRequest,
) -> ExcuseLetterResponse:
    """Student submits an excuse letter for an upcoming event."""
    school_id = getattr(current_user, "school_id", None)
    if not school_id:
        raise HTTPException(status_code=403, detail="User is not assigned to a school.")

    # Must be a student
    student_profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )
    if not student_profile:
        raise HTTPException(status_code=403, detail="Only students can submit excuse letters.")

    # Event must exist and belong to the same school
    event = db.query(Event).filter(Event.id == event_id, Event.school_id == school_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    # Server-side: event must still be Upcoming
    event_status = event.status.value if hasattr(event.status, "value") else str(event.status)
    if event_status != EventStatus.UPCOMING.value:
        raise HTTPException(
            status_code=400,
            detail="Excuse letters can only be submitted for upcoming events."
        )

    # One-per-student-per-event enforcement
    existing = (
        db.query(ExcuseLetter)
        .filter(
            ExcuseLetter.event_id == event_id,
            ExcuseLetter.student_profile_id == student_profile.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="You have already submitted an excuse letter for this event."
        )

    letter = ExcuseLetter(
        school_id=school_id,
        event_id=event_id,
        student_profile_id=student_profile.id,
        reason=payload.reason,
        attachment_path=payload.attachment_path,
        status=ExcuseLetterStatus.PENDING.value,
    )
    db.add(letter)
    db.flush()  # Get the ID before notifications

    # Reload with relations for notifications and response
    letter = _load_letter_with_relations(db, letter_id=letter.id)

    # Notify student
    event_name = event.name
    _notify_student(
        db,
        letter=letter,
        subject=f"Excuse Letter Submitted: {event_name}",
        message=(
            f"Hi {current_user.first_name or 'Student'},\n\n"
            f"Your excuse letter for {event_name} has been submitted and is now pending review.\n"
            "You will be notified once a decision is made.\n\n"
            "NEXUS"
        ),
    )

    # Notify relevant officers
    _notify_officers_new_submission(db, letter=letter)

    db.commit()
    db.refresh(letter)
    letter = _load_letter_with_relations(db, letter_id=letter.id)
    return _build_response(letter)


def get_excuse_letter_status_for_event(
    db: Session,
    *,
    current_user: User,
    event_id: int,
) -> ExcuseLetterStatusResponse:
    """Return this student's letter status for a given event (for the event card badge)."""
    student_profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )
    if not student_profile:
        return ExcuseLetterStatusResponse()

    letter = (
        db.query(ExcuseLetter)
        .filter(
            ExcuseLetter.event_id == event_id,
            ExcuseLetter.student_profile_id == student_profile.id,
        )
        .first()
    )
    if not letter:
        return ExcuseLetterStatusResponse()

    return ExcuseLetterStatusResponse(
        letter_id=letter.id,
        status=letter.status,
        reviewer_remarks=letter.reviewer_remarks,
        reviewed_at=letter.reviewed_at,
    )


def get_my_excuse_letters(
    db: Session,
    *,
    current_user: User,
) -> list[ExcuseLetterResponse]:
    """Return all excuse letters submitted by the current student."""
    student_profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )
    if not student_profile:
        return []

    from app.models.user import StudentProfile as SP
    letters = (
        db.query(ExcuseLetter)
        .options(
            joinedload(ExcuseLetter.event),
            joinedload(ExcuseLetter.student_profile).joinedload(SP.user),
            joinedload(ExcuseLetter.student_profile).joinedload(SP.program),
            joinedload(ExcuseLetter.reviewed_by_user),
        )
        .filter(ExcuseLetter.student_profile_id == student_profile.id)
        .order_by(ExcuseLetter.created_at.desc())
        .all()
    )
    return [_build_response(l) for l in letters]


def list_excuse_letters_for_event(
    db: Session,
    *,
    current_user: User,
    event_id: int,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[ExcuseLetterResponse]:
    """Officer: list all excuse letters for a given event within scope."""
    school_id = getattr(current_user, "school_id", None)
    if not school_id:
        raise HTTPException(status_code=403, detail="User is not assigned to a school.")

    event = db.query(Event).filter(Event.id == event_id, Event.school_id == school_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    if not _officer_can_review_event(db, current_user=current_user, event=event):
        raise HTTPException(status_code=403, detail="This event is outside your governance scope.")

    from app.models.user import StudentProfile as SP
    query = (
        db.query(ExcuseLetter)
        .options(
            joinedload(ExcuseLetter.event),
            joinedload(ExcuseLetter.student_profile).joinedload(SP.user),
            joinedload(ExcuseLetter.student_profile).joinedload(SP.program),
            joinedload(ExcuseLetter.reviewed_by_user),
        )
        .filter(ExcuseLetter.event_id == event_id)
    )
    if status_filter:
        query = query.filter(ExcuseLetter.status == status_filter)

    letters = query.order_by(ExcuseLetter.created_at.desc()).offset(skip).limit(limit).all()
    return [_build_response(l) for l in letters]


def list_all_excuse_letters(
    db: Session,
    *,
    current_user: User,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[ExcuseLetterResponse]:
    """Officer: list all excuse letters across events within scope (dashboard view)."""
    school_id = getattr(current_user, "school_id", None)
    if not school_id:
        raise HTTPException(status_code=403, detail="User is not assigned to a school.")

    from app.models.user import StudentProfile as SP
    query = (
        db.query(ExcuseLetter)
        .join(Event, Event.id == ExcuseLetter.event_id)
        .options(
            joinedload(ExcuseLetter.event),
            joinedload(ExcuseLetter.student_profile).joinedload(SP.user),
            joinedload(ExcuseLetter.student_profile).joinedload(SP.program),
            joinedload(ExcuseLetter.reviewed_by_user),
        )
        .filter(ExcuseLetter.school_id == school_id)
    )
    if status_filter:
        query = query.filter(ExcuseLetter.status == status_filter)

    letters = query.order_by(ExcuseLetter.created_at.desc()).offset(skip).limit(limit).all()

    # Filter by scope
    from app.core.security import has_any_role
    if has_any_role(current_user, ["admin", "campus_admin"]):
        return [_build_response(l) for l in letters]

    scoped = [l for l in letters if _officer_can_review_event(db, current_user=current_user, event=l.event)]
    return [_build_response(l) for l in scoped]


def get_excuse_letter_dashboard(
    db: Session,
    *,
    current_user: User,
) -> ExcuseLetterDashboardResponse:
    school_id = getattr(current_user, "school_id", None)
    if not school_id:
        raise HTTPException(status_code=403, detail="User is not assigned to a school.")

    all_letters = list_all_excuse_letters(db, current_user=current_user, limit=10000)
    total = len(all_letters)
    pending = sum(1 for l in all_letters if l.status == ExcuseLetterStatus.PENDING.value)
    approved = sum(1 for l in all_letters if l.status == ExcuseLetterStatus.APPROVED.value)
    rejected = sum(1 for l in all_letters if l.status == ExcuseLetterStatus.REJECTED.value)
    return ExcuseLetterDashboardResponse(total=total, pending=pending, approved=approved, rejected=rejected)


def _review_letter(
    db: Session,
    *,
    current_user: User,
    letter_id: int,
    new_status: ExcuseLetterStatus,
    payload: ExcuseLetterReviewRequest,
) -> ExcuseLetterResponse:
    if not _officer_has_review_permission(db, current_user=current_user):
        raise HTTPException(
            status_code=403,
            detail=(
                "You do not have the 'Review Excuse Letter' permission. "
                "Ask a Campus Admin to assign it to your governance role."
            ),
        )

    letter = _load_letter_with_relations(db, letter_id=letter_id)

    school_id = getattr(current_user, "school_id", None)
    if letter.school_id != school_id:
        raise HTTPException(status_code=404, detail="Excuse letter not found.")

    if not _officer_can_review_event(db, current_user=current_user, event=letter.event):
        raise HTTPException(status_code=403, detail="This event is outside your governance scope.")

    if letter.status != ExcuseLetterStatus.PENDING.value:
        raise HTTPException(
            status_code=409,
            detail="This excuse letter has already been decided and cannot be changed."
        )

    letter.status = new_status.value
    letter.reviewer_remarks = payload.remarks
    letter.reviewed_by_user_id = current_user.id
    letter.reviewed_at = utc_now()

    db.flush()

    # Notify student
    event_name = letter.event.name if letter.event else f"Event #{letter.event_id}"
    reviewer_name = " ".join(
        p for p in [
            getattr(current_user, "first_name", None),
            getattr(current_user, "last_name", None),
        ] if p
    ).strip() or current_user.email

    if new_status == ExcuseLetterStatus.APPROVED:
        subject = f"Excuse Letter Approved: {event_name}"
        message = (
            f"Hi {letter.student_profile.user.first_name if letter.student_profile and letter.student_profile.user else 'Student'},\n\n"
            f"Your excuse letter for {event_name} has been approved by {reviewer_name}.\n"
            + (f"Remarks: {payload.remarks}\n" if payload.remarks else "")
            + "\nNEXUS"
        )
    else:
        subject = f"Excuse Letter Rejected: {event_name}"
        message = (
            f"Hi {letter.student_profile.user.first_name if letter.student_profile and letter.student_profile.user else 'Student'},\n\n"
            f"Your excuse letter for {event_name} has been rejected by {reviewer_name}.\n"
            + (f"Reason: {payload.remarks}\n" if payload.remarks else "")
            + "\nNEXUS"
        )

    _notify_student(db, letter=letter, subject=subject, message=message)

    db.commit()
    db.refresh(letter)
    letter = _load_letter_with_relations(db, letter_id=letter.id)
    return _build_response(letter)


def approve_excuse_letter(
    db: Session,
    *,
    current_user: User,
    letter_id: int,
    payload: ExcuseLetterReviewRequest,
) -> ExcuseLetterResponse:
    return _review_letter(
        db,
        current_user=current_user,
        letter_id=letter_id,
        new_status=ExcuseLetterStatus.APPROVED,
        payload=payload,
    )


def reject_excuse_letter(
    db: Session,
    *,
    current_user: User,
    letter_id: int,
    payload: ExcuseLetterReviewRequest,
) -> ExcuseLetterResponse:
    return _review_letter(
        db,
        current_user=current_user,
        letter_id=letter_id,
        new_status=ExcuseLetterStatus.REJECTED,
        payload=payload,
    )


def upload_excuse_letter_attachment(
    db: Session,
    *,
    current_user: User,
    filename: str,
    file_bytes: bytes,
) -> str:
    """Save uploaded file and return a relative storage path."""
    from app.core.config import get_settings
    settings = get_settings()
    base_dir = os.path.join(settings.import_storage_dir, "excuse-letters")
    os.makedirs(base_dir, exist_ok=True)

    safe_filename = f"{current_user.id}_{utc_now().strftime('%Y%m%d%H%M%S')}_{filename}"
    dest = os.path.join(base_dir, safe_filename)
    with open(dest, "wb") as f:
        f.write(file_bytes)

    return f"excuse-letters/{safe_filename}"
