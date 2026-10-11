"""Campus Schemas.

Pydantic validation and serialization schemas for campuses and geographic boundaries.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CampusCollegeInfo(BaseModel):
    """Minimal college details embedded in campus response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    short_name: Optional[str] = None


class CampusBase(BaseModel):
    """Base schema for campus information."""

    name: str = Field(..., max_length=255, description="Campus name")
    address: str = Field(..., description="Physical address of campus")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    radius_meters: int = Field(
        3000, gt=0, description="Discovery perimeter radius in meters"
    )


class CampusResponse(CampusBase):
    """Serialized campus details with college association and business count."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    college_id: UUID
    college: Optional[CampusCollegeInfo] = None
    business_count: int = 0


class CampusListResponse(BaseModel):
    """List response for campuses."""

    items: List[CampusResponse]
    total: int
