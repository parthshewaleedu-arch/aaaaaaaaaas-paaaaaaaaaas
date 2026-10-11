"""Favorite Schemas

Pydantic schemas for student saved/bookmarked businesses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FavoriteItemResponse(BaseModel):
    """Schema representing a saved business item in student's favorites list."""

    business_id: UUID
    business_name: str
    category_name: Optional[str] = None
    rating: Optional[float] = None
    review_count: int = 0
    primary_photo_url: Optional[str] = None
    price_level: Optional[str] = None
    student_discount: bool = False
    is_open_now: Optional[bool] = None
    current_status: Optional[str] = None
    distance_meters: Optional[int] = None
    saved_at: datetime


class FavoriteListResponse(BaseModel):
    """Paginated list response for user favorites."""

    items: list[FavoriteItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class FavoriteStatusResponse(BaseModel):
    """Status check whether a business is favorited by the current user."""

    business_id: UUID
    is_favorite: bool


class FavoriteActionResponse(BaseModel):
    """Action response when adding or toggling a favorite."""

    success: bool
    message: str
    is_favorite: bool
