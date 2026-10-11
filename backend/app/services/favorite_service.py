"""Favorite Service

Business logic for managing student favorites, bookmarks, and saved business listings.
"""

from datetime import datetime, timezone
import math
from typing import Optional
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.business_photo import BusinessPhoto, BusinessPhotoStatus
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteItemResponse
from app.services.business_service import BusinessService


class FavoriteService:
    """Service for user favorites and bookmarking."""

    @classmethod
    def add_favorite(cls, user_id: UUID, business_id: UUID, db: Session) -> Favorite:
        """Add a business to student's favorites (idempotent).

        Args:
            user_id: Student user UUID.
            business_id: Target business UUID.
            db: Database session.

        Returns:
            Favorite model instance.
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError("Business not found")

        existing = (
            db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.business_id == business_id)
            .first()
        )
        if existing:
            return existing

        favorite = Favorite(
            user_id=user_id,
            business_id=business_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(favorite)
        db.commit()
        return favorite

    @classmethod
    def remove_favorite(cls, user_id: UUID, business_id: UUID, db: Session) -> bool:
        """Remove a business from student's favorites.

        Args:
            user_id: Student user UUID.
            business_id: Target business UUID.
            db: Database session.

        Returns:
            True if removed, False if not in favorites.
        """
        favorite = (
            db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.business_id == business_id)
            .first()
        )
        if not favorite:
            return False

        db.delete(favorite)
        db.commit()
        return True

    @classmethod
    def is_favorite(cls, user_id: UUID, business_id: UUID, db: Session) -> bool:
        """Check if a business is saved in student's favorites."""
        return (
            db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.business_id == business_id)
            .first()
            is not None
        )

    @classmethod
    def toggle_favorite(
        cls, user_id: UUID, business_id: UUID, db: Session
    ) -> tuple[bool, str]:
        """Toggle favorite status of a business.

        Returns:
            Tuple of (is_favorite_now, status_message).
        """
        if cls.is_favorite(user_id, business_id, db):
            cls.remove_favorite(user_id, business_id, db)
            return False, "Business removed from favorites"
        else:
            cls.add_favorite(user_id, business_id, db)
            return True, "Business added to favorites"

    @classmethod
    def calculate_distance(
        cls,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> int:
        """Calculate distance in meters between two lat/lng points using Haversine formula."""
        r = 6371000.0  # Earth's radius in meters
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
    def list_user_favorites(
        cls,
        user_id: UUID,
        db: Session,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[FavoriteItemResponse], int]:
        """List student's favorited businesses enriched with rating, distance, and live open status.

        Args:
            user_id: Student user UUID.
            db: Database session.
            user_lat: Optional user latitude for distance calculation.
            user_lng: Optional user longitude for distance calculation.
            page: 1-based page index.
            page_size: Items per page.

        Returns:
            Tuple of (favorite_items, total_count).
        """
        query = (
            db.query(Favorite, Business)
            .join(Business, Favorite.business_id == Business.id)
            .filter(
                Favorite.user_id == user_id,
                Business.deleted_at.is_(None),
            )
            .order_by(desc(Favorite.created_at))
        )

        total = query.count()
        skip = max(0, (page - 1) * page_size)
        rows = query.offset(skip).limit(page_size).all()

        items: list[FavoriteItemResponse] = []
        for fav, business in rows:
            # Primary photo or fallback first active photo
            photo = (
                db.query(BusinessPhoto)
                .filter(
                    BusinessPhoto.business_id == business.id,
                    BusinessPhoto.status == BusinessPhotoStatus.ACTIVE,
                )
                .order_by(
                    desc(BusinessPhoto.is_primary), desc(BusinessPhoto.created_at)
                )
                .first()
            )
            primary_photo_url = photo.image_url if photo else None

            # Primary category name
            category_name = business.categories[0].name if business.categories else None

            # Operating hours open status
            is_open_now, current_status = BusinessService.calculate_open_status(
                business.hours or []
            )

            # Distance calculation if user coordinates provided
            distance_meters = None
            if (
                user_lat is not None
                and user_lng is not None
                and business.latitude is not None
                and business.longitude is not None
            ):
                distance_meters = cls.calculate_distance(
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

            price_level_val = (
                business.price_level.value
                if hasattr(business.price_level, "value")
                else business.price_level
            )

            item = FavoriteItemResponse(
                business_id=business.id,
                business_name=business.name,
                category_name=category_name,
                rating=rating_val,
                review_count=business.review_count or 0,
                primary_photo_url=primary_photo_url,
                price_level=price_level_val,
                student_discount=business.student_discount or False,
                is_open_now=is_open_now,
                current_status=current_status,
                distance_meters=distance_meters,
                saved_at=fav.created_at,
            )
            items.append(item)

        return items, total
