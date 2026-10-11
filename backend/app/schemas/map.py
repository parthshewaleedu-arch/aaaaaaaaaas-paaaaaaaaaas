"""Map and Geospatial Schemas.

Pydantic schemas for map markers, viewport bounding boxes, campus maps, and directions.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.campus import CampusResponse


class BoundingBox(BaseModel):
    """Geographic bounding box for map viewports."""

    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lng: float = Field(..., ge=-180, le=180)
    max_lng: float = Field(..., ge=-180, le=180)


class MapMarkerResponse(BaseModel):
    """Lightweight map pin/marker for high-performance map rendering."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    latitude: float
    longitude: float
    distance_meters: Optional[int] = None
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
    average_rating: Optional[float] = None
    price_level: Optional[str] = None
    student_discount: bool = False
    primary_photo_url: Optional[str] = None
    is_open: Optional[bool] = None


class MapMarkersListResponse(BaseModel):
    """List response for map markers."""

    items: List[MapMarkerResponse]
    total: int
    bounding_box: Optional[BoundingBox] = None


class CampusMapResponse(BaseModel):
    """Map view payload for a selected campus."""

    campus: CampusResponse
    bounding_box: BoundingBox
    markers: List[MapMarkerResponse]
    total_markers: int


class DirectionsResponse(BaseModel):
    """Walking directions and relative navigation metadata."""

    business_id: UUID
    business_name: str
    destination_latitude: float
    destination_longitude: float
    user_latitude: float
    user_longitude: float
    distance_meters: int
    distance_km: float
    estimated_walking_minutes: int
    compass_bearing: str
    bearing_degrees: float
    google_maps_url: str
