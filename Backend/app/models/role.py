"""Use: Defines database models for role records and role permissions.
Where to use: Use this when the backend needs to store or load role records and role permissions data.
Role: Model layer. It maps Python objects to database tables and relationships.
"""

from sqlalchemy import BigInteger, Column, String
from app.models.base import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(BigInteger, primary_key=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)

    @property
    def name(self):
        return self.code
    
    @name.setter
    def name(self, value):
        self.code = value