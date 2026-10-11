"""Offer Service.

Core business logic for business discounts, student promotions, and redemption management.
"""

from datetime import datetime, timedelta, timezone
import secrets
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.business import Business
from app.models.category import Category
from app.models.offer import Offer, OfferStatus
from app.models.offer_redemption import OfferRedemption, OfferRedemptionStatus
from app.models.student import Student, VerificationStatus
from app.models.user import User, UserRole
from app.schemas.offer import (
    OfferCreate,
    OfferRedemptionValidateResponse,
    OfferUpdate,
)


class OfferService:
    """Service providing all CRUD operations for offers and student redemption lifecycle."""

    @classmethod
    def _generate_verification_code(cls, db: Session) -> str:
        """Generate a cryptographically secure, unique 8-character uppercase verification code."""
        for _ in range(10):
            # Format: OFR-XXXXXX
            code = f"OFR-{secrets.token_hex(3).upper()}"
            exists = (
                db.query(OfferRedemption)
                .filter(OfferRedemption.verification_code == code)
                .first()
            )
            if not exists:
                return code
        # Fallback to longer code if collisions occur
        return f"OFR-{secrets.token_hex(6).upper()}"

    @classmethod
    def create_offer(
        cls,
        business_id: UUID,
        offer_in: OfferCreate,
        current_user: User,
        db: Session,
    ) -> Offer:
        """Create a new promotional offer for a business.

        Only the business owner or platform admin may create offers.
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        if current_user.role != UserRole.ADMIN and business.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the business owner or platform admin can create offers for this business",
            )

        if offer_in.valid_until <= offer_in.valid_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offer valid_until must be strictly after valid_from",
            )

        offer = Offer(
            business_id=business_id,
            title=offer_in.title,
            description=offer_in.description,
            discount_type=offer_in.discount_type,
            discount_value=offer_in.discount_value,
            terms_conditions=offer_in.terms_conditions,
            valid_from=offer_in.valid_from,
            valid_until=offer_in.valid_until,
            max_redemptions=offer_in.max_redemptions,
            redemption_count=0,
            status=offer_in.status or OfferStatus.ACTIVE,
        )

        db.add(offer)
        db.commit()
        db.refresh(offer)
        return offer

    @classmethod
    def get_offer(
        cls,
        offer_id: UUID,
        db: Session,
        current_user: Optional[User] = None,
    ) -> Offer:
        """Retrieve details of a single offer by ID."""
        offer = (
            db.query(Offer)
            .options(joinedload(Offer.business))
            .filter(Offer.id == offer_id)
            .first()
        )
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        # Non-owners and public students can only view ACTIVE unexpired offers
        if offer.status != OfferStatus.ACTIVE:
            is_authorized = current_user and (
                current_user.role == UserRole.ADMIN
                or (offer.business and offer.business.owner_id == current_user.id)
            )
            if not is_authorized:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer not found or not active",
                )

        return offer

    @classmethod
    def list_offers(
        cls,
        db: Session,
        campus_id: Optional[UUID] = None,
        business_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None,
        status_filter: Optional[OfferStatus] = None,
        current_user: Optional[User] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Offer], int]:
        """List active offers with optional filtering by campus, business, category, or search keyword."""
        query = db.query(Offer).join(Business, Offer.business_id == Business.id)

        now = datetime.now(timezone.utc)

        # Default public visibility filter: ACTIVE and within validity dates
        if status_filter:
            query = query.filter(Offer.status == status_filter)
        else:
            query = query.filter(
                Offer.status == OfferStatus.ACTIVE,
                Offer.valid_from <= now,
                Offer.valid_until > now,
            )

        if campus_id:
            query = query.filter(Business.campus_id == campus_id)

        if business_id:
            query = query.filter(Offer.business_id == business_id)

        if category_id:
            query = query.filter(Business.categories.any(Category.id == category_id))

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                Offer.title.ilike(search_pattern)
                | Offer.description.ilike(search_pattern)
            )

        total = query.count()
        offers = (
            query.options(joinedload(Offer.business))
            .order_by(Offer.valid_until.asc(), Offer.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return offers, total

    @classmethod
    def update_offer(
        cls,
        offer_id: UUID,
        offer_update: OfferUpdate,
        current_user: User,
        db: Session,
    ) -> Offer:
        """Update an existing offer.

        Allowed only for business owner or platform admin.
        """
        offer = (
            db.query(Offer)
            .options(joinedload(Offer.business))
            .filter(Offer.id == offer_id)
            .first()
        )
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        if (
            current_user.role != UserRole.ADMIN
            and offer.business
            and offer.business.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this offer",
            )

        update_data = offer_update.model_dump(exclude_unset=True)

        valid_from = update_data.get("valid_from", offer.valid_from)
        valid_until = update_data.get("valid_until", offer.valid_until)
        if valid_until <= valid_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="valid_until must be strictly after valid_from",
            )

        for key, value in update_data.items():
            setattr(offer, key, value)

        offer.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(offer)
        return offer

    @classmethod
    def delete_or_cancel_offer(
        cls,
        offer_id: UUID,
        current_user: User,
        db: Session,
    ) -> Offer:
        """Cancel an offer.

        Marks offer status as CANCELLED to preserve historical records and redemptions.
        """
        offer = (
            db.query(Offer)
            .options(joinedload(Offer.business))
            .filter(Offer.id == offer_id)
            .first()
        )
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        if (
            current_user.role != UserRole.ADMIN
            and offer.business
            and offer.business.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this offer",
            )

        offer.status = OfferStatus.CANCELLED
        offer.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(offer)
        return offer

    @classmethod
    def redeem_offer(
        cls,
        offer_id: UUID,
        current_user: User,
        db: Session,
    ) -> OfferRedemption:
        """Redeem an active offer for a verified student.

        Generates a unique verification code and expiration timestamp.
        """
        # Role verification
        if (
            current_user.role != UserRole.STUDENT
            and current_user.role != UserRole.ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can redeem promotional offers",
            )

        # Check student verification status if student role
        if current_user.role == UserRole.STUDENT:
            student = (
                db.query(Student).filter(Student.user_id == current_user.id).first()
            )
            if (
                not student
                or student.verification_status != VerificationStatus.VERIFIED
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Student must be verified by college ID to redeem offers",
                )

        offer = (
            db.query(Offer)
            .options(joinedload(Offer.business))
            .filter(Offer.id == offer_id)
            .first()
        )
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        now = datetime.now(timezone.utc)

        # Check status and dates
        if offer.status != OfferStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Offer is not active (current status: {offer.status})",
            )

        if now < offer.valid_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offer validity has not yet started",
            )

        if now > offer.valid_until:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offer has expired",
            )

        # Check redemption limits
        if (
            offer.max_redemptions is not None
            and offer.redemption_count >= offer.max_redemptions
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offer has reached its maximum redemptions limit",
            )

        # Check if user already has an active pending redemption for this offer
        pending_redemption = (
            db.query(OfferRedemption)
            .filter(
                OfferRedemption.offer_id == offer_id,
                OfferRedemption.user_id == current_user.id,
                OfferRedemption.status == OfferRedemptionStatus.PENDING,
                OfferRedemption.expires_at > now,
            )
            .first()
        )
        if pending_redemption:
            # Return existing active pending redemption code without double-counting
            return pending_redemption

        # Generate unique code and code expiration
        code = cls._generate_verification_code(db)
        code_expires_at = min(now + timedelta(hours=2), offer.valid_until)

        redemption = OfferRedemption(
            offer_id=offer_id,
            user_id=current_user.id,
            redeemed_at=now,
            status=OfferRedemptionStatus.PENDING,
            verification_code=code,
            expires_at=code_expires_at,
        )

        offer.redemption_count = (offer.redemption_count or 0) + 1

        db.add(redemption)
        db.commit()
        db.refresh(redemption)
        return redemption

    @classmethod
    def validate_redemption(
        cls,
        business_id: UUID,
        verification_code: str,
        current_user: User,
        db: Session,
    ) -> OfferRedemptionValidateResponse:
        """Validate and mark completed an offer redemption presented to merchant.

        Only the business owner or platform admin can validate redemptions for this business.
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        if current_user.role != UserRole.ADMIN and business.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the business owner can validate redemptions for this business",
            )

        clean_code = verification_code.strip().upper()
        redemption = (
            db.query(OfferRedemption)
            .options(
                joinedload(OfferRedemption.offer),
                joinedload(OfferRedemption.user),
            )
            .filter(OfferRedemption.verification_code == clean_code)
            .first()
        )

        if not redemption:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid verification code",
            )

        if redemption.offer.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This offer code belongs to a different business",
            )

        if redemption.status == OfferRedemptionStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This redemption code has already been completed",
            )

        if redemption.status in (
            OfferRedemptionStatus.CANCELLED,
            OfferRedemptionStatus.EXPIRED,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This redemption is {redemption.status.lower()}",
            )

        now = datetime.now(timezone.utc)
        if redemption.expires_at and redemption.expires_at < now:
            redemption.status = OfferRedemptionStatus.EXPIRED
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This redemption code has expired",
            )

        # Mark as completed
        redemption.status = OfferRedemptionStatus.COMPLETED
        db.commit()
        db.refresh(redemption)

        # Format privacy-preserving student display name
        student = (
            db.query(Student).filter(Student.user_id == redemption.user_id).first()
        )
        student_display_name = (
            f"Student ({student.department or 'Verified'})"
            if student
            else "Verified Student"
        )

        return OfferRedemptionValidateResponse(
            success=True,
            message="Redemption successfully validated and completed.",
            redemption_id=redemption.id,
            offer_id=redemption.offer_id,
            offer_title=redemption.offer.title,
            discount_type=redemption.offer.discount_type,
            discount_value=float(redemption.offer.discount_value),
            student_id=redemption.user_id,
            student_display_name=student_display_name,
            status=OfferRedemptionStatus.COMPLETED,
        )

    @classmethod
    def list_user_redemptions(
        cls,
        user_id: UUID,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[OfferRedemption], int]:
        """List past and active redemptions for a student."""
        query = (
            db.query(OfferRedemption)
            .filter(OfferRedemption.user_id == user_id)
            .options(joinedload(OfferRedemption.offer).joinedload(Offer.business))
        )
        total = query.count()
        redemptions = (
            query.order_by(OfferRedemption.redeemed_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return redemptions, total

    @classmethod
    def list_business_offers(
        cls,
        business_id: UUID,
        db: Session,
        current_user: Optional[User] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Offer], int]:
        """List offers of a specific business.

        Owners and admins see all states; public users see only active unexpired offers.
        """
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        is_owner = current_user and (
            current_user.role == UserRole.ADMIN or business.owner_id == current_user.id
        )

        query = db.query(Offer).filter(Offer.business_id == business_id)
        if not is_owner:
            now = datetime.now(timezone.utc)
            query = query.filter(
                Offer.status == OfferStatus.ACTIVE,
                Offer.valid_from <= now,
                Offer.valid_until > now,
            )

        total = query.count()
        offers = (
            query.options(joinedload(Offer.business))
            .order_by(Offer.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return offers, total
