"""Map and Geospatial Service.

Provides geospatial algorithms, bounding box queries, map marker generation,
and navigation directions with compass bearing and walk time calculations.
"""

import math
from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.models.business import Business, BusinessStatus
from app.models.business_photo import BusinessPhoto, BusinessPhotoStatus
from app.models.category import Category
from app.schemas.map import (
    DirectionsResponse,
    MapMarkerResponse,
)
from app.services.business_service import BusinessService


class MapService:
    """Service handling map markers, spatial queries, and routing metadata."""

    @classmethod
    def calculate_distance(
        cls,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> int:
        """Calculate great-circle distance in meters between two lat/lng coordinates using Haversine."""
        r = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return int(r * c)

    @classmethod
    def calculate_bearing(
        cls,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> Tuple[float, str]:
        """Compute initial compass bearing in degrees (0-360) and 8-point cardinal abbreviation."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lambda = math.radians(lon2 - lon1)

        y = math.sin(delta_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - (
            math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
        )
        bearing_rad = math.atan2(y, x)
        bearing_deg = round((math.degrees(bearing_rad) + 360.0) % 360.0, 1)

        cardinals = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        cardinal_index = round(bearing_deg / 45.0) % 8
        cardinal_str = cardinals[cardinal_index]

        return bearing_deg, cardinal_str

    @classmethod
    def calculate_walking_minutes(
        cls,
        distance_meters: int,
        speed_kmh: float = 4.8,
    ) -> int:
        """Estimate walking time in minutes based on average walking speed (default 4.8 km/h)."""
        speed_meters_per_min = (speed_kmh * 1000.0) / 60.0
        return max(1, math.ceil(distance_meters / speed_meters_per_min))

    @classmethod
    def build_marker(
        cls,
        business: Business,
        db: Session,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
    ) -> MapMarkerResponse:
        """Convert a Business entity into a lightweight MapMarkerResponse."""
        # Find active primary cover photo
        primary_photo = (
            db.query(BusinessPhoto)
            .filter(
                BusinessPhoto.business_id == business.id,
                BusinessPhoto.status == BusinessPhotoStatus.ACTIVE,
            )
            .order_by(desc(BusinessPhoto.is_primary), desc(BusinessPhoto.created_at))
            .first()
        )
        photo_url = (
            primary_photo.image_url
            if (
                primary_photo
                and hasattr(primary_photo, "image_url")
                and isinstance(primary_photo.image_url, str)
            )
            else None
        )

        # Category metadata
        cat_name = business.categories[0].name if business.categories else None
        cat_slug = business.categories[0].slug if business.categories else None

        # Operating hours status
        is_open_now, _ = BusinessService.calculate_open_status(business.hours or [])

        # Distance calculation
        dist_meters = None
        if (
            user_lat is not None
            and user_lng is not None
            and business.latitude is not None
            and business.longitude is not None
        ):
            dist_meters = cls.calculate_distance(
                user_lat,
                user_lng,
                float(business.latitude),
                float(business.longitude),
            )

        rating_val = (
            float(business.average_rating)
            if business.average_rating is not None
            else None
        )
        price_val = (
            business.price_level.value
            if hasattr(business.price_level, "value")
            else business.price_level
        )

        return MapMarkerResponse(
            id=business.id,
            name=business.name,
            latitude=float(business.latitude),
            longitude=float(business.longitude),
            distance_meters=dist_meters,
            category_name=cat_name,
            category_slug=cat_slug,
            average_rating=rating_val,
            price_level=price_val,
            student_discount=bool(business.student_discount),
            primary_photo_url=photo_url,
            is_open=is_open_now,
        )

    @classmethod
    def get_markers_in_bounding_box(
        cls,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        db: Session,
        category_id: Optional[UUID] = None,
        student_discount: Optional[bool] = None,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
        limit: int = 150,
    ) -> List[MapMarkerResponse]:
        """Fetch all active business markers inside a geographical viewport bounding box."""
        query = (
            db.query(Business)
            .options(
                joinedload(Business.categories),
                joinedload(Business.hours),
            )
            .filter(
                Business.status == BusinessStatus.ACTIVE,
                Business.latitude >= min_lat,
                Business.latitude <= max_lat,
                Business.longitude >= min_lng,
                Business.longitude <= max_lng,
            )
        )

        if category_id:
            query = query.filter(Business.categories.any(Category.id == category_id))

        if student_discount is not None:
            query = query.filter(Business.student_discount == student_discount)

        businesses = query.limit(limit).all()

        markers = [
            cls.build_marker(b, db, user_lat=user_lat, user_lng=user_lng)
            for b in businesses
        ]

        if user_lat is not None and user_lng is not None:
            markers.sort(key=lambda m: (m.distance_meters or 9999999))

        return markers

    @classmethod
    def get_markers_within_radius(
        cls,
        latitude: float,
        longitude: float,
        radius_meters: int,
        db: Session,
        category_id: Optional[UUID] = None,
        student_discount: Optional[bool] = None,
        limit: int = 150,
    ) -> List[MapMarkerResponse]:
        """Fetch business markers within a circular radius from a coordinate point."""
        # Fast bounding box pre-filter
        delta_lat = radius_meters / 111320.0
        cos_lat = math.cos(math.radians(latitude))
        delta_lon = radius_meters / (111320.0 * max(0.01, cos_lat))

        candidates = cls.get_markers_in_bounding_box(
            min_lat=latitude - delta_lat,
            min_lng=longitude - delta_lon,
            max_lat=latitude + delta_lat,
            max_lng=longitude + delta_lon,
            category_id=category_id,
            student_discount=student_discount,
            user_lat=latitude,
            user_lng=longitude,
            limit=limit * 2,
            db=db,
        )

        # Precise circle distance filter
        filtered = [
            m
            for m in candidates
            if m.distance_meters is not None and m.distance_meters <= radius_meters
        ]
        return filtered[:limit]

    @classmethod
    def get_directions(
        cls,
        business_id: UUID,
        user_lat: float,
        user_lng: float,
        db: Session,
    ) -> DirectionsResponse:
        """Compute walking directions, estimated time, compass bearing, and Google Maps deep link."""
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        b_lat = float(business.latitude)
        b_lng = float(business.longitude)

        distance_meters = cls.calculate_distance(user_lat, user_lng, b_lat, b_lng)
        distance_km = round(distance_meters / 1000.0, 2)
        walking_minutes = cls.calculate_walking_minutes(distance_meters)
        bearing_degrees, compass_bearing = cls.calculate_bearing(
            user_lat, user_lng, b_lat, b_lng
        )

        # Deep link URL for Google Maps walking navigation
        google_maps_url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={user_lat:.6f},{user_lng:.6f}"
            f"&destination={b_lat:.6f},{b_lng:.6f}"
            f"&travelmode=walking"
        )

        return DirectionsResponse(
            business_id=business.id,
            business_name=business.name,
            destination_latitude=b_lat,
            destination_longitude=b_lng,
            user_latitude=user_lat,
            user_longitude=user_lng,
            distance_meters=distance_meters,
            distance_km=distance_km,
            estimated_walking_minutes=walking_minutes,
            compass_bearing=compass_bearing,
            bearing_degrees=bearing_degrees,
            google_maps_url=google_maps_url,
        )
