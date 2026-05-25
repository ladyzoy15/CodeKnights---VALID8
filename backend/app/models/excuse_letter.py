from __future__ import annotations

from enum import Enum as PyEnum

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.timezones import utc_now
from app.models.base import Base


class ExcuseLetterStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExcuseLetter(Base):
    __tablename__ = "excuse_letters"
    __table_args__ = (
        UniqueConstraint(
            "event_id", "student_profile_id",
            name="excuse_letters_event_id_student_profile_id_key"
        ),
    )

    id = Column(BigInteger, primary_key=True)
    school_id = Column(BigInteger, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(BigInteger, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    student_profile_id = Column(BigInteger, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    attachment_path = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default=ExcuseLetterStatus.PENDING.value, index=True)
    reviewed_by_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewer_remarks = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    # Relationships
    school = relationship("School")
    event = relationship("Event")
    student_profile = relationship("StudentProfile")
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by_user_id])
