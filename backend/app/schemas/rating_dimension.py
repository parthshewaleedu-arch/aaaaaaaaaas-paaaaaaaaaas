"""Rating Dimension Schemas

Validation and serialization schemas for category-specific evaluation dimensions.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RatingDimensionBase(BaseModel):
    """Base rating dimension schema."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: int = Field(0, ge=0)


class RatingDimensionCreate(BaseModel):
    """Schema for creating a category evaluation dimension."""

    category_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = None
    description: Optional[str] = None
    display_order: int = Field(0, ge=0)


class RatingDimensionResponse(BaseModel):
    """Schema for rating dimension response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: Optional[UUID] = None
    name: str
    slug: str
    description: Optional[str] = None
    display_order: int
