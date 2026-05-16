"""Use: Defines database models for schools, school settings, and school audit logs.
Where to use: Use this when the backend needs to store or load schools, school settings, and school audit logs data.
Role: Model layer. It maps Python objects to database tables and relationships.
"""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.event_defaults import (
    DEFAULT_EVENT_EARLY_CHECK_IN_MINUTES,
    DEFAULT_EVENT_LATE_THRESHOLD_MINUTES,
    DEFAULT_EVENT_SIGN_OUT_GRACE_MINUTES,
)
from app.models.base import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(BigInteger, primary_key=True, index=True)
    
    # Normalized schema column names
    legal_name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False, index=True)
    
    @property
    def school_id(self):
        return self.id
    
    @property
    def name(self):
        return self.legal_name
    
    @name.setter
    def name(self, value):
        self.legal_name = value

    @property
    def school_name(self):
        return self.display_name
    
    @school_name.setter
    def school_name(self, value):
        self.display_name = value
    
    school_code = Column(String(50), nullable=True, unique=True, index=True)
    address = Column(String(500), nullable=False)
    
    # These fields are moved to school_branding in normalized schema, 
    # but we keep them here as aliases/columns for backward compatibility if possible,
    # or map them to the new tables if they are used as relationships.
    # For now, let's just make sure the core fields exist.
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Legacy fields that are now in separate tables
    logo_url = Column(String(1000), nullable=True) 
    primary_color = Column(String(7), nullable=False, default="#162F65")
    secondary_color = Column(String(7), nullable=True)
    subscription_status = Column(String(30), nullable=False, default="trial")
    
    @property
    def active_status(self):
        return self.is_active
    
    @active_status.setter
    def active_status(self, value):
        self.is_active = value
    # subscription_plan = Column(String(100), nullable=False, default="free")
    # subscription_start = Column(Date, nullable=False, default=date.today)
    # subscription_end = Column(Date, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    settings = relationship(
        "SchoolSetting",
        back_populates="school",
        uselist=False,
        cascade="all, delete-orphan",
    )
    branding = relationship(
        "SchoolBranding",
        back_populates="school",
        uselist=False,
        cascade="all, delete-orphan",
    )
    event_policy = relationship(
        "SchoolEventPolicy",
        back_populates="school",
        uselist=False,
        cascade="all, delete-orphan",
    )
    users = relationship("User", back_populates="school")
    student_profiles = relationship("StudentProfile", back_populates="school")
    events = relationship("Event", back_populates="school")
    event_types = relationship("EventType", back_populates="school")
    audit_logs = relationship(
        "SchoolAuditLog",
        back_populates="school",
        cascade="all, delete-orphan",
    )


class SchoolSetting(Base):
    __tablename__ = "school_settings"

    school_id = Column(
        BigInteger,
        ForeignKey("schools.id", ondelete="CASCADE"),
        primary_key=True,
    )
    primary_color = Column(String(7), nullable=False, default="#162F65")
    secondary_color = Column(String(7), nullable=False, default="#2C5F9E")
    accent_color = Column(String(7), nullable=False, default="#4A90E2")
    event_default_early_check_in_minutes = Column(
        Integer,
        nullable=False,
        default=DEFAULT_EVENT_EARLY_CHECK_IN_MINUTES,
    )
    event_default_late_threshold_minutes = Column(
        Integer,
        nullable=False,
        default=DEFAULT_EVENT_LATE_THRESHOLD_MINUTES,
    )
    event_default_sign_out_grace_minutes = Column(
        Integer,
        nullable=False,
        default=DEFAULT_EVENT_SIGN_OUT_GRACE_MINUTES,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    updated_by_user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    school = relationship("School", back_populates="settings")


class SchoolAuditLog(Base):
    __tablename__ = "school_audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    school_id = Column(
        BigInteger,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(100), nullable=False)
    status = Column(String(30), nullable=False, default="success")
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    school = relationship("School", back_populates="audit_logs")


class SchoolBranding(Base):
    __tablename__ = "school_branding"

    school_id = Column(
        BigInteger,
        ForeignKey("schools.id", ondelete="CASCADE"),
        primary_key=True,
    )
    logo_url = Column(String(1000), nullable=True)
    primary_color = Column(String(7), nullable=False, default="#162F65")
    secondary_color = Column(String(7), nullable=True)
    accent_color = Column(String(7), nullable=True)

    school = relationship("School", back_populates="branding")


class SchoolEventPolicy(Base):
    __tablename__ = "school_event_policies"

    school_id = Column(
        BigInteger,
        ForeignKey("schools.id", ondelete="CASCADE"),
        primary_key=True,
    )
    default_early_check_in_minutes = Column(
        Integer,
        nullable=False,
        default=DEFAULT_EVENT_EARLY_CHECK_IN_MINUTES,
    )
    default_late_threshold_minutes = Column(
        Integer,
        nullable=False,
        default=DEFAULT_EVENT_LATE_THRESHOLD_MINUTES,
    )
    default_sign_out_grace_minutes = Column(
        Integer,
        nullable=False,
        default=DEFAULT_EVENT_SIGN_OUT_GRACE_MINUTES,
    )

    school = relationship("School", back_populates="event_policy")
