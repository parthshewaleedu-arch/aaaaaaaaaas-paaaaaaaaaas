"""Business Owner Dashboard Endpoints.

Dedicated routes for business owners and administrators to inspect
performance analytics, customer conversion metrics, and consolidated listings.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_owner_user
from app.core.database import get_db
from app.models.business import Business
from app.models.user import User, UserRole
from app.schemas.owner_analytics import (
    BusinessAnalyticsResponse,
    BusinessSummaryCard,
    OwnerDashboardResponse,
)
from app.services.owner_analytics_service import OwnerAnalyticsService

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=OwnerDashboardResponse,
    summary="Get business owner dashboard metrics",
)
def get_owner_dashboard(
    current_user: User = Depends(get_current_owner_user),
    db: Session = Depends(get_db),
):
    """Retrieve consolidated KPIs and listing performance cards for owner."""
    return OwnerAnalyticsService.get_owner_dashboard(
        db=db,
        owner_id=current_user.id,
    )


@router.get(
    "/businesses",
    response_model=List[BusinessSummaryCard],
    summary="List owner businesses with summary metrics",
)
def list_owner_businesses(
    current_user: User = Depends(get_current_owner_user),
    db: Session = Depends(get_db),
):
    """Retrieve all business listings owned by the current user with key performance indicators."""
    dashboard = OwnerAnalyticsService.get_owner_dashboard(
        db=db,
        owner_id=current_user.id,
    )
    return dashboard.businesses


@router.get(
    "/businesses/{business_id}/analytics",
    response_model=BusinessAnalyticsResponse,
    summary="Get comprehensive analytics for an owned business",
)
def get_business_analytics(
    business_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Time window in days"),
    current_user: User = Depends(get_current_owner_user),
    db: Session = Depends(get_db),
):
    """Retrieve deep analytics for a specific business owned by the user or viewed by admin."""
    business = (
        db.query(Business)
        .filter(Business.id == business_id, Business.deleted_at.is_(None))
        .first()
    )
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    if business.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this business",
        )

    return OwnerAnalyticsService.get_business_analytics(
        db=db,
        business_id=business_id,
        days=days,
    )
