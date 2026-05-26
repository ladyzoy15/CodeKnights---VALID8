from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.timezones import utc_now
from app.models.base import Base

class ExcuseLetter(Base):
    __tablename__ = "excuse_letters"

    id = Column(BigInteger, primary_key=True)
    student_profile_id = Column(BigInteger, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(BigInteger, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    attachment_url = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default="Pending")  # Pending, Approved, Rejected
    reviewer_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewer_remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    student = relationship("StudentProfile")
    event = relationship("Event")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
