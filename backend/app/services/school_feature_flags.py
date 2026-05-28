"""Use: Contains logic for checking school-level feature flags.
Where to use: Use this from routers or other services when school-specific feature availability must be checked.
Role: Service layer. It abstracts feature gating logic.
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from app.models.school import School, SchoolEventPolicy


def _get_school_event_policy(db: Session, school_id: int) -> SchoolEventPolicy:
    """Load or create the event policy (settings) for a school."""
    policy = db.query(SchoolEventPolicy).filter(SchoolEventPolicy.school_id == school_id).first()
    if policy:
        return policy
    
    # Create default policy if missing
    policy = SchoolEventPolicy(school_id=school_id)
    db.add(policy)
    db.flush()
    return policy


def privileged_face_verification_enabled_for_school(
    db: Session,
    school_id: int | None,
) -> bool:
    """Check if a school has privileged face verification enabled."""
    if school_id is None:
        # Platform admins (global) are always allowed if the global flag is on.
        return True
        
    policy = _get_school_event_policy(db, school_id)
    return bool(policy.privileged_face_verification_enabled)


def attendance_face_recognition_enabled_for_school(
    db: Session,
    school_id: int | None,
) -> bool:
    """Check if a school has attendance face recognition enabled."""
    if school_id is None:
        return True
        
    policy = _get_school_event_policy(db, school_id)
    return bool(policy.attendance_face_recognition_enabled)


def first_time_face_registration_required_for_school(
    db: Session,
    school_id: int | None,
) -> bool:
    """Check if a school requires face registration on first login."""
    if school_id is None:
        return True
        
    policy = _get_school_event_policy(db, school_id)
    return bool(policy.first_time_face_registration_required)
