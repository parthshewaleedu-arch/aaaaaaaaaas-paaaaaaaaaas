"""Business Schemas

Pydantic schemas for business validation and serialization.
"""

from datetime import datetime, time
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.business_photo import BusinessPhotoResponse
from app.schemas.service import ServiceResponse


class BusinessBase(BaseModel):
    """Base business schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    phone: str = Field(..., min_length=10, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    website_url: Optional[str] = None
    address: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    price_level: Optional[str] = Field(None, pattern=r"^₹{1,4}$")
    student_discount: bool = False
    student_discount_description: Optional[str] = None


class BusinessCreate(BusinessBase):
    """Schema for creating a business."""

    campus_id: UUID
    category_ids: list[UUID] = []


class BusinessUpdate(BaseModel):
    """Schema for updating a business."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    website_url: Optional[str] = None
    address: Optional[str] = Field(None, min_length=1)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    price_level: Optional[str] = Field(None, pattern=r"^₹{1,4}$")
    student_discount: Optional[bool] = None
    student_discount_description: Optional[str] = None


class BusinessHoursItem(BaseModel):
    """Schema for individual day operating hours entry."""

    day_of_week: int = Field(
        ..., ge=0, le=6, description="0=Sunday, 1=Monday, ..., 6=Saturday"
    )
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_closed: bool = False


class BusinessHoursCreate(BusinessHoursItem):
    """Schema for creating business hours."""

    pass


class BusinessHoursBatchUpdate(BaseModel):
    """Schema for updating business hours for multiple or all days."""

    hours: list[BusinessHoursItem] = Field(
        ..., description="List of operating hours per day"
    )


class BusinessHoursResponse(BaseModel):
    """Schema for business hours response."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    day_of_week: int
    day_name: Optional[str] = None
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_closed: bool = False


class BusinessHoursScheduleResponse(BaseModel):
    """Schema for full business schedule response including open status."""

    is_open_now: bool = False
    current_status: Optional[str] = None
    hours: list[BusinessHoursResponse] = []


class BusinessCategoryResponse(BaseModel):
    """Schema for business category response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    parent_id: Optional[UUID] = None


class BusinessResponse(BaseModel):
    """Schema for business response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    campus_id: UUID
    name: str
    description: Optional[str] = None
    phone: str
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    status: str
    verification_status: str
    price_level: Optional[str] = None
    student_discount: bool
    student_discount_description: Optional[str] = None
    average_rating: Optional[float] = None
    review_count: int
    verified_at: Optional[Union[datetime, str]] = None
    verification_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    distance_meters: Optional[int] = None
    is_open_now: Optional[bool] = None
    current_status: Optional[str] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None


class BusinessDetailResponse(BusinessResponse):
    """Schema for detailed business response with relations."""

    categories: list[BusinessCategoryResponse] = []
    hours: list[BusinessHoursResponse] = []
    photos: list[BusinessPhotoResponse] = []
    services: list[ServiceResponse] = []
    is_open_now: Optional[bool] = None
    current_status: Optional[str] = None
    rating_breakdown: Optional[dict[str, float]] = None


class BusinessListResponse(BaseModel):
    """Schema for paginated business list response."""

    items: list[BusinessResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BusinessVerificationRequest(BaseModel):
    """Schema for business verification submission."""

    documents: list[str] = Field(
        default=[], description="URLs to uploaded business proof documents"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes or comments from owner"
    )


class BusinessStatusUpdate(BaseModel):
    """Schema for updating business status (admin)."""

    status: str = Field(..., pattern=r"^(PENDING|ACTIVE|SUSPENDED|REJECTED|REMOVED)$")
    reason: Optional[str] = None


class BusinessVerificationUpdate(BaseModel):
    """Schema for updating business verification (admin)."""

    action: Optional[str] = Field(
        None, pattern=r"^(APPROVE|REJECT)$", description="Verification decision action"
    )
    verification_status: Optional[str] = Field(
        None, pattern=r"^(UNVERIFIED|PENDING|VERIFIED|EXPIRED)$"
    )
    reason: Optional[str] = Field(
        None, description="Explanation or approval/rejection reason"
    )
