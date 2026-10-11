"""Map Endpoints.

REST API routes for interactive map markers, viewport bounding queries, and geospatial overlays.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.campus import Campus
from app.schemas.campus import CampusBase
from app.schemas.map import (
    BoundingBox,
    MapMarkersListResponse,
)
from app.services.map_service import MapService

router = APIRouter()


class CampusMapOverlayItem(CampusBase):
    id: UUID


@router.get(
    "/markers",
    response_model=MapMarkersListResponse,
    summary="Get lightweight business map markers within viewport or radius",
)
def get_map_markers(
    min_lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Viewport minimum latitude"
    ),
    min_lng: Optional[float] = Query(
        None, ge=-180, le=180, description="Viewport minimum longitude"
    ),
    max_lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Viewport maximum latitude"
    ),
    max_lng: Optional[float] = Query(
        None, ge=-180, le=180, description="Viewport maximum longitude"
    ),
    latitude: Optional[float] = Query(
        None, ge=-90, le=90, description="Center latitude for radius query"
    ),
    longitude: Optional[float] = Query(
        None, ge=-180, le=180, description="Center longitude for radius query"
    ),
    radius_meters: Optional[int] = Query(
        3000, ge=50, le=50000, description="Search radius in meters"
    ),
    category_id: Optional[UUID] = Query(None, description="Filter by category UUID"),
    student_discount: Optional[bool] = Query(
        None, description="Filter by student discount availability"
    ),
    limit: int = Query(150, ge=1, le=500, description="Max pins to return"),
    db: Session = Depends(get_db),
):
    """Query lightweight map markers optimized for interactive map rendering and clustering.

    Supports either viewport bounding box (min_lat, min_lng, max_lat, max_lng)
    or center radius (latitude, longitude, radius_meters).
    """
    bbox = None
    if (
        min_lat is not None
        and min_lng is not None
        and max_lat is not None
        and max_lng is not None
    ):
        if min_lat > max_lat or min_lng > max_lng:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bounding box: min coordinates must be <= max coordinates",
            )
        bbox = BoundingBox(
            min_lat=min_lat,
            min_lng=min_lng,
            max_lat=max_lat,
            max_lng=max_lng,
        )
        markers = MapService.get_markers_in_bounding_box(
            min_lat=min_lat,
            min_lng=min_lng,
            max_lat=max_lat,
            max_lng=max_lng,
            category_id=category_id,
            student_discount=student_discount,
            user_lat=latitude,
            user_lng=longitude,
            limit=limit,
            db=db,
        )
    elif latitude is not None and longitude is not None:
        markers = MapService.get_markers_within_radius(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters or 3000,
            category_id=category_id,
            student_discount=student_discount,
            limit=limit,
            db=db,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Must provide either bounding box (min_lat, min_lng, max_lat, max_lng) "
                "or center coordinates (latitude, longitude)"
            ),
        )

    return MapMarkersListResponse(
        items=markers,
        total=len(markers),
        bounding_box=bbox,
    )


@router.get(
    "/campuses",
    response_model=List[CampusMapOverlayItem],
    summary="Get campus boundary coordinates for map overlays",
)
def get_campuses_map_overlays(
    db: Session = Depends(get_db),
):
    """Retrieve all campus coordinates and coverage radii for interactive map layer overlays.

    Public endpoint.
    """
    campuses = db.query(Campus).all()
    return [
        CampusMapOverlayItem(
            id=c.id,
            name=c.name,
            address=c.address,
            latitude=float(c.latitude),
            longitude=float(c.longitude),
            radius_meters=c.radius_meters or 3000,
        )
        for c in campuses
    ]
