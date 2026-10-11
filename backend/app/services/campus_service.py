"""Campus Service.

Business logic for managing colleges, campus profiles, geographical coverage, and map data.
"""

import math
from typing import List, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.business import Business, BusinessStatus
from app.models.campus import Campus
from app.schemas.campus import (
    CampusCollegeInfo,
    CampusResponse,
)
from app.schemas.map import (
    BoundingBox,
    CampusMapResponse,
    MapMarkerResponse,
)
from app.services.map_service import MapService


class CampusService:
    """Service providing campus management and campus map view data."""

    @classmethod
    def list_campuses(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[CampusResponse], int]:
        """List all registered campuses with attached college information and business counts."""
        query = db.query(Campus).options(joinedload(Campus.college))
        total = query.count()
        campuses = query.offset(skip).limit(limit).all()

        results: List[CampusResponse] = []
        for campus in campuses:
            biz_count = (
                db.query(Business)
                .filter(
                    Business.campus_id == campus.id,
                    Business.status == BusinessStatus.ACTIVE,
                )
                .count()
            )

            college_info = (
                CampusCollegeInfo(
                    id=campus.college.id,
                    name=campus.college.name,
                    short_name=campus.college.short_name,
                )
                if campus.college
                else None
            )

            results.append(
                CampusResponse(
                    id=campus.id,
                    college_id=campus.college_id,
                    name=campus.name,
                    address=campus.address,
                    latitude=float(campus.latitude),
                    longitude=float(campus.longitude),
                    radius_meters=campus.radius_meters or 3000,
                    college=college_info,
                    business_count=biz_count,
                )
            )

        return results, total

    @classmethod
    def get_campus_by_id(
        cls,
        campus_id: UUID,
        db: Session,
    ) -> CampusResponse:
        """Retrieve a single campus by ID."""
        campus = (
            db.query(Campus)
            .options(joinedload(Campus.college))
            .filter(Campus.id == campus_id)
            .first()
        )
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campus not found",
            )

        biz_count = (
            db.query(Business)
            .filter(
                Business.campus_id == campus.id,
                Business.status == BusinessStatus.ACTIVE,
            )
            .count()
        )

        college_info = (
            CampusCollegeInfo(
                id=campus.college.id,
                name=campus.college.name,
                short_name=campus.college.short_name,
            )
            if campus.college
            else None
        )

        return CampusResponse(
            id=campus.id,
            college_id=campus.college_id,
            name=campus.name,
            address=campus.address,
            latitude=float(campus.latitude),
            longitude=float(campus.longitude),
            radius_meters=campus.radius_meters or 3000,
            college=college_info,
            business_count=biz_count,
        )

    @classmethod
    def get_campus_map_data(
        cls,
        campus_id: UUID,
        db: Session,
    ) -> CampusMapResponse:
        """Retrieve campus coordinate center, discovery bounding box, and active business map markers."""
        campus_resp = cls.get_campus_by_id(campus_id, db)

        lat = campus_resp.latitude
        lon = campus_resp.longitude
        radius = float(campus_resp.radius_meters)

        delta_lat = radius / 111320.0
        cos_lat = math.cos(math.radians(lat))
        delta_lon = radius / (111320.0 * max(0.01, cos_lat))

        bbox = BoundingBox(
            min_lat=round(lat - delta_lat, 6),
            max_lat=round(lat + delta_lat, 6),
            min_lng=round(lon - delta_lon, 6),
            max_lng=round(lon + delta_lon, 6),
        )

        businesses = (
            db.query(Business)
            .options(
                joinedload(Business.categories),
                joinedload(Business.hours),
            )
            .filter(
                Business.campus_id == campus_id,
                Business.status == BusinessStatus.ACTIVE,
            )
            .all()
        )

        markers: List[MapMarkerResponse] = [
            MapService.build_marker(b, db, user_lat=lat, user_lng=lon)
            for b in businesses
        ]

        markers.sort(key=lambda m: (m.distance_meters or 9999999))

        return CampusMapResponse(
            campus=campus_resp,
            bounding_box=bbox,
            markers=markers,
            total_markers=len(markers),
        )
