"""College Model

Represents colleges/universities in the system.
"""

from sqlalchemy import Column, Enum, String, Text
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class CollegeStatus(str, enum.Enum):
    """College status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"


class College(BaseModel):
    """College/University model.

    Represents educational institutions whose students use the platform.
    Email domain is used for student verification.
    """

    __tablename__ = "colleges"

    # Basic information
    name = Column(String(255), nullable=False)
    short_name = Column(String(100), nullable=True)

    # Verification
    email_domain = Column(String(100), nullable=False, unique=True, index=True)

    # Additional information
    website_url = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)

    # Status
    status = Column(
        Enum(CollegeStatus, name="college_status", create_type=True),
        nullable=False,
        default=CollegeStatus.ACTIVE,
        index=True,
    )

    # Relationships
    campuses = relationship(
        "Campus",
        back_populates="college",
        cascade="all, delete-orphan",
    )
    students = relationship(
        "Student",
        back_populates="college",
    )

    def __repr__(self):
        return f"<College(id={self.id}, name={self.name})>"
