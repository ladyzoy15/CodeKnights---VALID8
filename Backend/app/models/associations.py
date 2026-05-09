"""Use: Defines database models for many-to-many link tables.
Where to use: Use this when the backend needs to store or load many-to-many link tables data.
Role: Model layer. It maps Python objects to database tables and relationships.
"""

# app/models/associations.py
from sqlalchemy import Table, Column, BigInteger, ForeignKey
from app.models.base import Base

# Many-to-many association tables - Named to match normalized schema
event_department_association = Table(
    "event_departments",
    Base.metadata,
    Column("event_id", BigInteger, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("department_id", BigInteger, ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True)
)

event_program_association = Table(
    "event_programs",
    Base.metadata,
    Column("event_id", BigInteger, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("program_id", BigInteger, ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True)
)

program_department_association = Table(
    "program_departments",
    Base.metadata,
    Column("program_id", BigInteger, ForeignKey("programs.id", ondelete="CASCADE"), primary_key=True),
    Column("department_id", BigInteger, ForeignKey("departments.id", ondelete="CASCADE"), primary_key=True)
)
