"""Business Photo Schemas

Pydantic validation schemas for business photos, gallery listings, and uploads.
"""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BusinessPhotoBase(BaseModel):
    """Base schema for business photo."""

    image_url: str = Field(..., max_length=1000, description="URL of the photo")
    caption: Optional[str] = Field(
        None, max_length=255, description="Photo description or caption"
    )
    is_primary: bool = Field(
        False, description="Whether this photo is the main featured cover image"
    )


class BusinessPhotoCreate(BusinessPhotoBase):
    """Schema for uploading a business photo."""

    pass


class BusinessPhotoResponse(BaseModel):
    """Schema for serialized business photo response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    image_url: str
    caption: Optional[str] = None
    is_primary: bool = False
    uploader_type: str = "OWNER"
    status: str = "ACTIVE"
    uploaded_by: UUID
    created_at: Optional[Union[datetime, str]] = None


class BusinessPhotoListResponse(BaseModel):
    """List response for business gallery photos."""

    items: list[BusinessPhotoResponse]
    total: int
