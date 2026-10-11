"""Offer Endpoints.

REST API routes for discovering, redeeming, and managing promotional offers.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.models.offer import OfferStatus
from app.models.user import User
from app.schemas.offer import (
    OfferListResponse,
    OfferRedeemResponse,
    OfferRedemptionListResponse,
    OfferResponse,
    OfferUpdate,
)
from app.services.offer_service import OfferService

router = APIRouter()


@router.get(
    "",
    response_model=OfferListResponse,
    summary="List active promotional offers",
)
def list_offers(
    campus_id: Optional[UUID] = Query(None, description="Filter by campus"),
    business_id: Optional[UUID] = Query(None, description="Filter by business"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    status: Optional[OfferStatus] = Query(
        None, description="Filter by status (default: ACTIVE)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Get active promotional offers with optional campus, category, or business filters.

    Public endpoint.
    """
    skip = (page - 1) * limit
    offers, total = OfferService.list_offers(
        db=db,
        campus_id=campus_id,
        business_id=business_id,
        category_id=category_id,
        search=search,
        status_filter=status,
        skip=skip,
        limit=limit,
    )
    return OfferListResponse(
        items=offers,
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/my-redemptions",
    response_model=OfferRedemptionListResponse,
    summary="List current student's offer redemptions",
)
def get_my_redemptions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve history of all offer redemptions initiated by current student.

    Requires authenticated STUDENT role.
    """
    skip = (page - 1) * limit
    redemptions, total = OfferService.list_user_redemptions(
        user_id=current_user.id,
        db=db,
        skip=skip,
        limit=limit,
    )
    return OfferRedemptionListResponse(items=redemptions, total=total)


@router.get(
    "/{offer_id}",
    response_model=OfferResponse,
    summary="Get offer details",
)
def get_offer_details(
    offer_id: UUID,
    db: Session = Depends(get_db),
):
    """Get detailed information of a specific promotional offer.

    Public endpoint.
    """
    return OfferService.get_offer(offer_id=offer_id, db=db)


@router.patch(
    "/{offer_id}",
    response_model=OfferResponse,
    summary="Update offer details",
)
def update_offer(
    offer_id: UUID,
    offer_update: OfferUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update title, discount, validity, or status of an existing offer.

    Requires business owner or platform admin privileges.
    """
    return OfferService.update_offer(
        offer_id=offer_id,
        offer_update=offer_update,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/{offer_id}",
    response_model=OfferResponse,
    summary="Cancel promotional offer",
)
def cancel_offer(
    offer_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Cancel an active promotional offer.

    Requires business owner or platform admin privileges.
    """
    return OfferService.delete_or_cancel_offer(
        offer_id=offer_id,
        current_user=current_user,
        db=db,
    )


@router.post(
    "/{offer_id}/redeem",
    response_model=OfferRedeemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Redeem promotional offer (verified students)",
    dependencies=[
        Depends(rate_limit(limit=20, window_seconds=60, key_prefix="redeem_offer"))
    ],
)
def redeem_offer(
    offer_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Redeem an offer and generate a unique verification code to present to merchant.

    Requires authenticated and verified STUDENT role.
    """
    redemption = OfferService.redeem_offer(
        offer_id=offer_id,
        current_user=current_user,
        db=db,
    )
    return OfferRedeemResponse(
        success=True,
        redemption_id=redemption.id,
        offer_id=redemption.offer_id,
        verification_code=redemption.verification_code,
        expires_at=redemption.expires_at,
        status=redemption.status,
        message="Offer redeemed. Show verification code to merchant.",
    )
