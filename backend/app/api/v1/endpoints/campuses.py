"""Campus Endpoints.

REST API routes for campus discovery, boundary configurations, and map view data.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.campus import (
    CampusListResponse,
    CampusResponse,
)
from app.schemas.map import CampusMapResponse
from app.services.campus_service import CampusService

router = APIRouter()


@router.get(
    "",
    response_model=CampusListResponse,
    summary="List all registered college campuses",
)
def list_campuses(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    db: Session = Depends(get_db),
):
    """Retrieve list of campuses with geographic center coordinates and active business counts.

    Public endpoint.
    """
    campuses, total = CampusService.list_campuses(db=db, skip=skip, limit=limit)
    return CampusListResponse(items=campuses, total=total)


@router.get(
    "/{campus_id}",
    response_model=CampusResponse,
    summary="Get campus details by ID",
)
def get_campus(
    campus_id: UUID,
    db: Session = Depends(get_db),
):
    """Retrieve detailed information, boundaries, and associated college for a specific campus.

    Public endpoint.
    """
    return CampusService.get_campus_by_id(campus_id=campus_id, db=db)


@router.get(
    "/{campus_id}/map",
    response_model=CampusMapResponse,
    summary="Get interactive map view for a campus",
)
def get_campus_map(
    campus_id: UUID,
    db: Session = Depends(get_db),
):
    """Retrieve campus coordinates, calculated discovery bounding box, and active business pins.

    Public endpoint optimized for campus map viewers.
    """
    return CampusService.get_campus_map_data(campus_id=campus_id, db=db)
