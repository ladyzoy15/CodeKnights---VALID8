"""Use: Defines database models for attendance records.
Where to use: Use this when the backend needs to store or load attendance records data.
Role: Model layer. It maps Python objects to database tables and relationships.
"""




from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, String, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime
from enum import Enum

class AttendanceMethod(str, Enum):
    FACE_SCAN = "face_scan"
    MANUAL = "manual"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    EXCUSED = "excused"
    INCOMPLETE = "incomplete"

class AttendanceMethodLookup(Base):
    __tablename__ = "attendance_methods"
    code = Column(String(50), primary_key=True)
    display_name = Column(String(100), nullable=False)

class AttendanceStatusLookup(Base):
    __tablename__ = "attendance_statuses"
    code = Column(String(20), primary_key=True)
    display_name = Column(String(100), nullable=False)

class Attendance(Base):
    __tablename__ = "attendance_records"

    id = Column(BigInteger, primary_key=True, index=True)
    # Normalized schema column names
    student_profile_id = Column(BigInteger, ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True)
    event_id = Column(BigInteger, ForeignKey("events.id", ondelete="CASCADE"), index=True)
    time_in = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    time_out = Column(DateTime(timezone=True))
    
    method_code = Column(String(50))  # "face_scan", "manual", etc.
    status_code = Column(String(20), nullable=False, default='present')
    
    @property
    def student_id(self):
        return self.student_profile_id
    
    @student_id.setter
    def student_id(self, value):
        self.student_profile_id = value

    @property
    def method(self):
        return self.method_code
    
    @method.setter
    def method(self, value):
        self.method_code = value

    @property
    def status(self):
        return self.status_code
    
    @status.setter
    def status(self, value):
        self.status_code = value

    check_in_status = Column(String(16), nullable=True)
    check_out_status = Column(String(16), nullable=True)
    
    verified_by_user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    
    @property
    def verified_by(self):
        return self.verified_by_user_id
    
    @verified_by.setter
    def verified_by(self, value):
        self.verified_by_user_id = value
    
    notes = Column(String(500))
    geo_distance_m = Column(Float, nullable=True)
    geo_effective_distance_m = Column(Float, nullable=True)
    geo_latitude = Column(Float, nullable=True)
    geo_longitude = Column(Float, nullable=True)
    geo_accuracy_m = Column(Float, nullable=True)
    liveness_label = Column(String(32), nullable=True)
    liveness_score = Column(Float, nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="attendances")
    event = relationship("Event", back_populates="attendances")
