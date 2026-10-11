"""Student Model

Student-specific profile information linked to User.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class VerificationStatus(str, enum.Enum):
    """Verification status enumeration."""

    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"


class Student(BaseModel):
    """Student profile model.

    Extended profile information for users with STUDENT role.
    One-to-one relationship with User model.
    """

    __tablename__ = "students"

    # User relationship (one-to-one)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # College and campus
    college_id = Column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    campus_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campuses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Profile information
    full_name = Column(String(255), nullable=False)
    profile_photo_url = Column(Text, nullable=True)

    # Academic information (optional)
    student_id = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)

    # Verification
    verification_status = Column(
        Enum(VerificationStatus, name="verification_status", create_type=True),
        nullable=False,
        default=VerificationStatus.UNVERIFIED,
        index=True,
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Email verification for college email
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="student", uselist=False)
    college = relationship("College", back_populates="students")
    campus = relationship("Campus", back_populates="students")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "year IS NULL OR (year >= 1 AND year <= 7)",
            name="ck_students_year",
        ),
    )

    def __repr__(self):
        return f"<Student(id={self.id}, full_name={self.full_name})>"
