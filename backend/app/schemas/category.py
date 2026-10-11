"""Category Schemas

Pydantic schemas for category validation and serialization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base category schema."""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    slug: Optional[str] = Field(None, max_length=100, description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Category description")
    icon: Optional[str] = Field(
        None, max_length=100, description="Icon identifier or URL"
    )
    display_order: int = Field(0, ge=0, description="Sorting order in UI")
    is_active: bool = Field(True, description="Whether the category is active")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    parent_id: Optional[UUID] = Field(
        None, description="Optional parent category ID for hierarchy"
    )


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[UUID] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """Schema for category responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool
    display_order: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CategoryTreeResponse(BaseModel):
    """Schema for hierarchical category response with children."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool
    display_order: int
    children: list["CategoryTreeResponse"] = []


class CategoryListResponse(BaseModel):
    """Schema for list of categories."""

    items: list[CategoryResponse]
    total: int
