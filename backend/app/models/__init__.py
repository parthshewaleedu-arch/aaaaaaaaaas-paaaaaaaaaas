"""Models Package

Exports all SQLAlchemy models for easy importing.
"""

from app.models.base import BaseModel
from app.models.user import User, UserRole, UserStatus
from app.models.college import College, CollegeStatus
from app.models.campus import Campus
from app.models.student import Student, VerificationStatus
from app.models.business import (
    Business,
    BusinessStatus,
    BusinessVerificationStatus,
    PriceLevel,
)

__all__ = [
    # Base
    "BaseModel",

    # User
    "User",
    "UserRole",
    "UserStatus",

    # College
    "College",
    "CollegeStatus",

    # Campus
    "Campus",

    # Student
    "Student",
    "VerificationStatus",

    # Business
    "Business",
    "BusinessStatus",
    "BusinessVerificationStatus",
    "PriceLevel",
]
