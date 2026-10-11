"""Business Service

Business logic for business management.
"""

from datetime import datetime, timezone
import json

import math
from typing import Optional, Union
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.business import (
    Business,
    BusinessStatus,
    BusinessVerificationStatus,
    PriceLevel,
)
from app.models.business_hours import BusinessHours, DAY_NAMES
from app.models.category import Category
from app.models.campus import Campus
from app.models.user import User, UserRole
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessHoursItem


class BusinessService:
    """Service for managing businesses."""

    @staticmethod
    def calculate_distance_meters(
        lat1: float, lon1: float, lat2: float, lon2: float
    ) -> int:
        """Calculate Great-Circle distance between two coordinates in meters.

        Args:
            lat1: Origin latitude
            lon1: Origin longitude
            lat2: Destination latitude
            lon2: Destination longitude

        Returns:
            Distance in meters
        """
        r = 6371000  # Earth radius in meters
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

    @staticmethod
    def create_business(
        business_data: BusinessCreate, owner_id: UUID, db: Session
    ) -> Business:
        """Create a new business.

        Args:
            business_data: Business creation data
            owner_id: Owner's user ID
            db: Database session

        Returns:
            Created Business instance
        """
        # Verify owner exists and has OWNER role
        owner = db.query(User).filter(User.id == owner_id).first()
        if not owner:
            raise ValueError("Owner not found")
        if owner.role != UserRole.OWNER:
            raise ValueError("User must have OWNER role")

        # Verify campus exists
        campus = db.query(Campus).filter(Campus.id == business_data.campus_id).first()
        if not campus:
            raise ValueError("Campus not found")

        # Verify categories exist if provided
        if business_data.category_ids:
            categories = (
                db.query(Category)
                .filter(Category.id.in_(business_data.category_ids))
                .all()
            )
            if len(categories) != len(business_data.category_ids):
                raise ValueError("One or more categories not found")

        # Create business
        business = Business(
            owner_id=owner_id,
            campus_id=business_data.campus_id,
            name=business_data.name,
            description=business_data.description,
            phone=business_data.phone,
            whatsapp=business_data.whatsapp,
            email=business_data.email,
            website_url=business_data.website_url,
            address=business_data.address,
            latitude=business_data.latitude,
            longitude=business_data.longitude,
            price_level=PriceLevel(business_data.price_level)
            if business_data.price_level
            else None,
            student_discount=business_data.student_discount,
            student_discount_description=business_data.student_discount_description,
            status=BusinessStatus.PENDING,
            verification_status=BusinessVerificationStatus.UNVERIFIED,
        )

        db.add(business)
        db.flush()  # Get the ID

        # Add categories
        if business_data.category_ids:
            for category_id in business_data.category_ids:
                category = db.query(Category).filter(Category.id == category_id).first()
                if category:
                    business.categories.append(category)

        db.commit()
        db.refresh(business)
        return business

    @classmethod
    def get_business_by_id(cls, business_id: UUID, db: Session) -> Optional[Business]:
        """Get business by ID.

        Args:
            business_id: Business UUID
            db: Database session

        Returns:
            Business instance or None
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        return cls.enrich_business_details(business) if business else None

    @classmethod
    def get_business_by_owner(cls, owner_id: UUID, db: Session) -> Optional[Business]:
        """Get business by owner ID.

        Args:
            owner_id: Owner's user ID
            db: Database session

        Returns:
            Business instance or None
        """
        business = db.query(Business).filter(Business.owner_id == owner_id).first()
        return cls.enrich_business_details(business) if business else None

    @staticmethod
    def update_business(
        business_id: UUID, business_data: BusinessUpdate, db: Session
    ) -> Optional[Business]:
        """Update business.

        Args:
            business_id: Business UUID
            business_data: Business update data
            db: Database session

        Returns:
            Updated Business instance or None
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return None

        update_data = business_data.model_dump(exclude_unset=True)

        # Handle price_level enum conversion
        if "price_level" in update_data and update_data["price_level"]:
            update_data["price_level"] = PriceLevel(update_data["price_level"])

        for field, value in update_data.items():
            setattr(business, field, value)

        db.commit()
        db.refresh(business)
        return business

    @staticmethod
    def delete_business(business_id: UUID, db: Session) -> bool:
        """Delete business (soft delete).

        Args:
            business_id: Business UUID
            db: Database session

        Returns:
            True if deleted, False if not found
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return False

        business.status = BusinessStatus.REMOVED
        business.deleted_at = datetime.now(timezone.utc)
        db.commit()
        return True

    @classmethod
    def list_businesses(
        cls,
        db: Session,
        campus_id: Optional[UUID] = None,
        status: Optional[BusinessStatus] = None,
        verification_status: Optional[BusinessVerificationStatus] = None,
        category_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
        search: Optional[str] = None,
        min_rating: Optional[float] = None,
        price_level: Optional[str] = None,
        student_discount: Optional[bool] = None,
        verified_only: Optional[bool] = None,
        open_now: Optional[bool] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_meters: Optional[int] = None,
        sort: Optional[str] = "newest",
        skip: int = 0,
        limit: int = 20,
    ) -> list[Business]:
        """List and search businesses with comprehensive filters.

        Args:
            db: Database session
            campus_id: Filter by campus
            status: Filter by business status
            verification_status: Filter by verification status
            category_id: Filter by category (includes subcategories)
            owner_id: Filter by owner
            search: Keyword search on name and description
            min_rating: Filter by minimum average rating
            price_level: Filter by price level
            student_discount: Filter by student discount availability
            verified_only: Filter for verified businesses only
            open_now: Filter for currently open businesses
            latitude: Latitude for geospatial search
            longitude: Longitude for geospatial search
            radius_meters: Search radius in meters
            sort: Sort criteria (relevance, rating, distance, newest, name)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Business instances
        """
        query = db.query(Business)

        if campus_id:
            query = query.filter(Business.campus_id == campus_id)
        if status:
            query = query.filter(Business.status == status)
        if verification_status:
            query = query.filter(Business.verification_status == verification_status)
        if verified_only:
            query = query.filter(
                Business.verification_status == BusinessVerificationStatus.VERIFIED
            )
        if owner_id:
            query = query.filter(Business.owner_id == owner_id)

        # Keyword text search across name and description
        if search:
            search_clean = f"%{search.strip()}%"
            query = query.filter(
                (Business.name.ilike(search_clean))
                | (Business.description.ilike(search_clean))
            )

        # Filter by minimum rating
        if min_rating is not None:
            query = query.filter(Business.average_rating >= min_rating)

        # Filter by price level
        if price_level:
            query = query.filter(Business.price_level == PriceLevel(price_level))

        # Filter by student discount
        if student_discount is not None:
            query = query.filter(Business.student_discount == student_discount)

        # Category filter (hierarchical: includes direct category and subcategories)
        if category_id:
            subcategories = (
                db.query(Category.id).filter(Category.parent_id == category_id).all()
            )
            category_ids = [category_id] + [s[0] for s in subcategories]
            query = (
                query.join(Business.categories)
                .filter(Category.id.in_(category_ids))
                .distinct()
            )

        # Geospatial filter (if PostGIS location exists)
        if latitude is not None and longitude is not None and radius_meters is not None:
            try:
                from sqlalchemy import text

                query = query.filter(
                    text(
                        "location IS NOT NULL AND ST_DWithin("
                        "location, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :radius)"
                    )
                ).params(lat=latitude, lon=longitude, radius=radius_meters)
            except Exception:
                pass

        # Database-level sorting
        if sort == "rating":
            query = query.order_by(
                Business.average_rating.desc().nullslast(), Business.review_count.desc()
            )
        elif sort == "name":
            query = query.order_by(Business.name.asc())
        elif sort == "newest":
            query = query.order_by(Business.created_at.desc())
        else:
            query = query.order_by(Business.created_at.desc())

        items = query.offset(skip).limit(limit).all()

        # Compute distance_meters and in-memory sort by distance if requested
        if latitude is not None and longitude is not None:
            for b in items:
                if b.latitude is not None and b.longitude is not None:
                    b.distance_meters = cls.calculate_distance_meters(
                        latitude, longitude, float(b.latitude), float(b.longitude)
                    )
            if sort == "distance":
                items.sort(
                    key=lambda b: getattr(b, "distance_meters", float("inf"))
                    or float("inf")
                )

        # Enrich all items with dynamic properties (is_open_now, current_status)
        for b in items:
            cls.enrich_business_details(b)

        # Filter by open_now status if requested
        if open_now is not None:
            items = [b for b in items if getattr(b, "is_open_now", False) == open_now]

        return items

    @classmethod
    def count_businesses(
        cls,
        db: Session,
        campus_id: Optional[UUID] = None,
        status: Optional[BusinessStatus] = None,
        verification_status: Optional[BusinessVerificationStatus] = None,
        category_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
        search: Optional[str] = None,
        min_rating: Optional[float] = None,
        price_level: Optional[str] = None,
        student_discount: Optional[bool] = None,
        verified_only: Optional[bool] = None,
        open_now: Optional[bool] = None,
    ) -> int:
        """Count businesses with optional filters.

        Args:
            db: Database session
            campus_id: Filter by campus
            status: Filter by business status
            verification_status: Filter by verification status
            category_id: Filter by category
            owner_id: Filter by owner
            search: Search query
            min_rating: Minimum rating
            price_level: Price level
            student_discount: Student discount availability
            verified_only: Verified only

        Returns:
            Count of businesses
        """
        query = db.query(Business)

        if campus_id:
            query = query.filter(Business.campus_id == campus_id)
        if status:
            query = query.filter(Business.status == status)
        if verification_status:
            query = query.filter(Business.verification_status == verification_status)
        if verified_only:
            query = query.filter(
                Business.verification_status == BusinessVerificationStatus.VERIFIED
            )
        if owner_id:
            query = query.filter(Business.owner_id == owner_id)

        if search:
            search_clean = f"%{search.strip()}%"
            query = query.filter(
                (Business.name.ilike(search_clean))
                | (Business.description.ilike(search_clean))
            )

        if min_rating is not None:
            query = query.filter(Business.average_rating >= min_rating)

        if price_level:
            query = query.filter(Business.price_level == PriceLevel(price_level))

        if student_discount is not None:
            query = query.filter(Business.student_discount == student_discount)

        if category_id:
            subcategories = (
                db.query(Category.id).filter(Category.parent_id == category_id).all()
            )
            category_ids = [category_id] + [s[0] for s in subcategories]
            query = (
                query.join(Business.categories)
                .filter(Category.id.in_(category_ids))
                .distinct()
            )

        return query.count()

    @staticmethod
    def submit_for_verification(
        business_id: UUID,
        owner_id: UUID,
        db: Session,
        notes: Optional[str] = None,
        documents: Optional[list[str]] = None,
    ) -> Optional[Business]:
        """Submit business for verification.

        Args:
            business_id: Business UUID
            owner_id: Owner's user ID (for authorization)
            db: Database session
            notes: Optional submission notes from owner
            documents: Optional list of verification document URLs

        Returns:
            Updated Business instance or None
        """
        business = (
            db.query(Business)
            .filter(Business.id == business_id, Business.owner_id == owner_id)
            .first()
        )
        if not business:
            return None

        if business.verification_status == BusinessVerificationStatus.VERIFIED:
            raise ValueError("Business is already verified")

        if business.verification_status == BusinessVerificationStatus.PENDING:
            raise ValueError("Business already submitted for verification")

        business.verification_status = BusinessVerificationStatus.PENDING
        business.status = BusinessStatus.PENDING

        # Store verification notes/documents metadata
        if notes or documents:
            payload = {}
            if notes:
                payload["notes"] = notes
            if documents:
                payload["documents"] = documents
            business.verification_notes = json.dumps(payload)

        # Clear previous rejection reason upon new submission
        business.rejection_reason = None

        db.commit()
        db.refresh(business)
        return business

    @staticmethod
    def approve_business(
        business_id: UUID,
        db: Session,
        reviewer_id: Optional[UUID] = None,
        reason: Optional[str] = None,
    ) -> Optional[Business]:
        """Approve business verification (admin).

        Args:
            business_id: Business UUID
            db: Database session
            reviewer_id: Admin user ID who reviewed
            reason: Optional approval notes

        Returns:
            Updated Business instance or None
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return None

        business.verification_status = BusinessVerificationStatus.VERIFIED
        business.status = BusinessStatus.ACTIVE
        business.verified_at = datetime.now(timezone.utc)
        business.rejection_reason = None

        db.commit()
        db.refresh(business)
        return business

    @staticmethod
    def reject_business(
        business_id: UUID,
        db: Session,
        reviewer_id: Optional[UUID] = None,
        reason: Optional[str] = None,
    ) -> Optional[Business]:
        """Reject business verification (admin).

        Args:
            business_id: Business UUID
            db: Database session
            reviewer_id: Admin user ID who reviewed
            reason: Reason for rejection

        Returns:
            Updated Business instance or None
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return None

        business.verification_status = BusinessVerificationStatus.UNVERIFIED
        business.status = BusinessStatus.REJECTED
        business.rejection_reason = (
            reason or "Verification submission was rejected by administrator"
        )

        db.commit()
        db.refresh(business)
        return business

    @staticmethod
    def suspend_business(
        business_id: UUID,
        db: Session,
        reviewer_id: Optional[UUID] = None,
        reason: Optional[str] = None,
    ) -> Optional[Business]:
        """Suspend business (admin).

        Args:
            business_id: Business UUID
            db: Database session
            reviewer_id: Admin user ID
            reason: Suspension reason

        Returns:
            Updated Business instance or None
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return None

        business.status = BusinessStatus.SUSPENDED
        if reason:
            business.rejection_reason = reason

        db.commit()
        db.refresh(business)
        return business

    @staticmethod
    def check_ownership(business_id: UUID, owner_id: UUID, db: Session) -> bool:
        """Check if user owns the business.

        Args:
            business_id: Business UUID
            owner_id: Owner's user ID
            db: Database session

        Returns:
            True if user owns business, False otherwise
        """
        business = (
            db.query(Business)
            .filter(Business.id == business_id, Business.owner_id == owner_id)
            .first()
        )
        return business is not None

    @classmethod
    def enrich_business_details(
        cls, business: Optional[Business]
    ) -> Optional[Business]:
        """Enrich a business model instance with dynamic properties.

        Computes is_open_now, current_status, and calculates days_since_update
        for each service offering.

        Args:
            business: The Business instance to enrich.

        Returns:
            The enriched Business instance.
        """
        if not business:
            return business

        hours = getattr(business, "hours", []) or []
        is_open, current_status = cls.calculate_open_status(hours)
        business.is_open_now = is_open
        business.current_status = current_status

        # Calculate days_since_update for attached services
        services = getattr(business, "services", []) or []
        if services:
            from app.services.service_service import ServiceService

            for s in services:
                s.days_since_update = ServiceService.calculate_days_since_update(
                    s.updated_at
                )

        # Ensure only active photos are included
        photos = getattr(business, "photos", []) or []
        if photos:
            from app.models.business_photo import BusinessPhotoStatus

            business.photos = [
                p
                for p in photos
                if getattr(p, "status", None) == BusinessPhotoStatus.ACTIVE
            ]

        return business

    @classmethod
    def set_business_hours(
        cls,
        business_id: UUID,
        hours_data: list[Union[dict, BusinessHoursItem]],
        db: Session,
    ) -> list[BusinessHours]:
        """Set or update weekly operating hours for a business.

        Replaces existing hours with the newly provided schedule.
        Validates day_of_week and timing constraints.

        Args:
            business_id: Business UUID.
            hours_data: List of daily hours configurations.
            db: Database session.

        Returns:
            List of created/updated BusinessHours records.
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError("Business not found")

        validated_items = []
        for item in hours_data:
            if isinstance(item, dict):
                day = item.get("day_of_week")
                open_t = item.get("open_time")
                close_t = item.get("close_time")
                is_closed = item.get("is_closed", False)
            else:
                day = item.day_of_week
                open_t = item.open_time
                close_t = item.close_time
                is_closed = item.is_closed

            if day is None or not (0 <= day <= 6):
                raise ValueError(
                    f"Invalid day_of_week: {day}. Must be between 0 (Sunday) and 6 (Saturday)"
                )

            if not is_closed:
                if open_t is None or close_t is None:
                    raise ValueError(
                        f"Open and close times required for day {day} when not closed"
                    )

            validated_items.append(
                {
                    "day_of_week": day,
                    "open_time": open_t if not is_closed else None,
                    "close_time": close_t if not is_closed else None,
                    "is_closed": is_closed,
                }
            )

        # Remove existing hours for this business
        db.query(BusinessHours).filter(BusinessHours.business_id == business_id).delete(
            synchronize_session=False
        )

        # Insert new hours
        new_hours = []
        for item in validated_items:
            h = BusinessHours(
                id=uuid4(),
                business_id=business_id,
                day_of_week=item["day_of_week"],
                open_time=item["open_time"],
                close_time=item["close_time"],
                is_closed=item["is_closed"],
            )
            db.add(h)
            new_hours.append(h)

        db.commit()
        for h in new_hours:
            db.refresh(h)
        return sorted(new_hours, key=lambda x: x.day_of_week)

    @classmethod
    def get_business_hours(cls, business_id: UUID, db: Session) -> list[BusinessHours]:
        """Get operating hours schedule for a business.

        Args:
            business_id: Business UUID.
            db: Database session.

        Returns:
            List of BusinessHours ordered by day_of_week.
        """
        return (
            db.query(BusinessHours)
            .filter(BusinessHours.business_id == business_id)
            .order_by(BusinessHours.day_of_week.asc())
            .all()
        )

    @staticmethod
    def calculate_open_status(
        hours: list[BusinessHours],
        now: Optional[datetime] = None,
    ) -> tuple[bool, str]:
        """Determine whether business is open now and provide descriptive status.

        Args:
            hours: List of business hours objects for the business.
            now: Optional current datetime to test against (UTC or localized).

        Returns:
            Tuple of (is_open_now: bool, current_status: str)
        """
        if not hours:
            return False, "Hours not available"

        if now is None:
            now = datetime.now(timezone.utc)

        # Map Python weekday (0=Mon, 6=Sun) to our schema (0=Sun, 1=Mon, ..., 6=Sat)
        current_day = (now.weekday() + 1) % 7
        current_time = now.time()

        # Find schedule for today
        today_hours = [h for h in hours if h.day_of_week == current_day]

        if not today_hours or all(h.is_closed for h in today_hours):
            next_status = BusinessService._find_next_open_time(hours, current_day)
            return False, f"Closed • {next_status}" if next_status else "Closed today"

        for h in today_hours:
            if not h.is_closed and h.open_time and h.close_time:
                # Normal daytime shift: open_time <= close_time
                if h.open_time <= h.close_time:
                    if h.open_time <= current_time < h.close_time:
                        close_str = h.close_time.strftime("%I:%M %p").lstrip("0")
                        return True, f"Open until {close_str}"
                    elif current_time < h.open_time:
                        open_str = h.open_time.strftime("%I:%M %p").lstrip("0")
                        return False, f"Closed • Opens at {open_str}"
                else:
                    # Overnight shift: e.g. 20:00 to 02:00
                    if current_time >= h.open_time or current_time < h.close_time:
                        close_str = h.close_time.strftime("%I:%M %p").lstrip("0")
                        return True, f"Open until {close_str}"

        # Closed for the rest of today
        next_status = BusinessService._find_next_open_time(hours, current_day)
        return False, f"Closed • {next_status}" if next_status else "Closed"

    @staticmethod
    def _find_next_open_time(
        hours: list[BusinessHours], current_day: int
    ) -> Optional[str]:
        """Find the next upcoming open time from the schedule."""
        for offset in range(1, 8):
            day = (current_day + offset) % 7
            day_matches = [
                h
                for h in hours
                if h.day_of_week == day and not h.is_closed and h.open_time
            ]
            if day_matches:
                first_open = sorted(day_matches, key=lambda x: x.open_time)[0]
                day_name = DAY_NAMES[day] if day < len(DAY_NAMES) else "upcoming day"
                time_str = first_open.open_time.strftime("%I:%M %p").lstrip("0")
                if offset == 1:
                    return f"Opens tomorrow at {time_str}"
                return f"Opens {day_name} at {time_str}"
        return None
