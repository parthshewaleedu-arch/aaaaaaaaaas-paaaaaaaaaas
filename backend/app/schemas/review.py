"""Review Schemas

Validation and serialization schemas for student reviews, dimensional ratings,
photos, business owner responses, and moderation reports.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewRatingItem(BaseModel):
    """Schema for submitting or updating an individual dimensional rating score."""

    dimension_id: UUID
    rating: int = Field(..., ge=1, le=5, description="Score from 1 to 5")


class ReviewRatingResponse(BaseModel):
    """Schema for individual dimensional rating score in response."""

    model_config = ConfigDict(from_attributes=True)

    dimension_id: UUID
    dimension: Optional[str] = None
    rating: int


class ReviewPhotoResponse(BaseModel):
    """Schema for photo attached to a review."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    image_url: str
    created_at: Optional[datetime] = None


class ReviewResponseItem(BaseModel):
    """Schema for owner's response to a review."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    response_text: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReviewUserResponse(BaseModel):
    """Schema for anonymous/verified student reviewer info."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    display_name: str
    is_verified_student: bool = False


class ReviewCreate(BaseModel):
    """Schema for submitting a student review."""

    overall_rating: int = Field(
        ..., ge=1, le=5, description="Overall satisfaction score from 1 to 5"
    )
    review_text: Optional[str] = Field(
        None, max_length=5000, description="Written review comments"
    )
    ratings: list[ReviewRatingItem] = Field(
        default=[], description="Category-specific dimensional ratings"
    )
    photo_urls: list[str] = Field(
        default=[], description="URLs to attached photo evidence"
    )


class ReviewUpdate(BaseModel):
    """Schema for updating an existing student review."""

    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=5000)
    ratings: Optional[list[ReviewRatingItem]] = None
    photo_urls: Optional[list[str]] = None


class ReviewDetailResponse(BaseModel):
    """Detailed review response with reviewer status, ratings, photos, and owner response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    user: ReviewUserResponse
    overall_rating: int
    review_text: Optional[str] = None
    verification_level: str
    status: str
    ratings: list[ReviewRatingResponse] = []
    photos: list[ReviewPhotoResponse] = []
    helpful_count: int = 0
    has_response: bool = False
    response: Optional[ReviewResponseItem] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReviewListResponse(BaseModel):
    """Paginated list of reviews with multi-dimensional rating breakdown."""

    items: list[ReviewDetailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    rating_breakdown: Optional[dict[str, float]] = None


class ReviewOwnerResponseCreate(BaseModel):
    """Schema for business owner responding to a review."""

    response_text: str = Field(
        ..., min_length=1, max_length=2000, description="Owner's public reply"
    )


class ReviewReportCreate(BaseModel):
    """Schema for reporting a review to administrators."""

    reason: str = Field(
        ...,
        pattern=r"^(SPAM|FAKE_REVIEW|HARASSMENT|PERSONAL_INFORMATION|ABUSE|IRRELEVANT|EXTORTION|OTHER)$",
        description="Reason code for report",
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Details supporting the report"
    )


class ReviewReportResponse(BaseModel):
    """Schema for review moderation report response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    review_id: UUID
    reported_by: UUID
    reason: str
    description: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
