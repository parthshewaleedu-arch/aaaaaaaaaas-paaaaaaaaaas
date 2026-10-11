"""Student Schemas

Pydantic schemas for student profile validation and serialization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    """Base student schema with common fields."""

    full_name: str = Field(..., min_length=1, max_length=255)
    student_id: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1, le=7)
    profile_photo_url: Optional[str] = None


class StudentCreate(StudentBase):
    """Schema for creating a student profile."""

    user_id: UUID
    college_id: UUID
    campus_id: Optional[UUID] = None


class StudentUpdate(BaseModel):
    """Schema for updating a student profile."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    student_id: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1, le=7)
    profile_photo_url: Optional[str] = None
    campus_id: Optional[UUID] = None


class StudentResponse(StudentBase):
    """Schema for student profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    college_id: UUID
    campus_id: Optional[UUID] = None
    verification_status: str
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class StudentProfileResponse(BaseModel):
    """Schema for student profile response with user info."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    student_id: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = None
    profile_photo_url: Optional[str] = None
    college_id: UUID
    college_name: str
    campus_id: Optional[UUID] = None
    campus_name: Optional[str] = None
    verification_status: str
    verified_at: Optional[datetime] = None
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime


class StudentVerificationResponse(BaseModel):
    """Schema for student verification status response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    verification_status: str
    verified_at: Optional[datetime] = None
    is_email_verified: bool
