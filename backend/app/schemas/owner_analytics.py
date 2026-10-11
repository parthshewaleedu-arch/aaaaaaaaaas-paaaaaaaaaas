"""Owner Analytics and Interaction Schemas.

Validation and serialization schemas for merchant engagement metrics,
interaction events, and owner dashboard summaries.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InteractionTypeEnum(str, Enum):
    """Types of customer engagement interactions."""

    PROFILE_VIEW = "PROFILE_VIEW"
    DIRECTION_CLICK = "DIRECTION_CLICK"
    CALL_CLICK = "CALL_CLICK"
    OFFER_VIEW = "OFFER_VIEW"
    SEARCH_APPEARANCE = "SEARCH_APPEARANCE"


class BusinessInteractionCreate(BaseModel):
    """Payload to record customer action on a business profile."""

    interaction_type: InteractionTypeEnum = Field(
        ...,
        description=(
            "Type of engagement action: PROFILE_VIEW, DIRECTION_CLICK, CALL_CLICK, OFFER_VIEW, SEARCH_APPEARANCE"
        ),
    )


class BusinessInteractionResponse(BaseModel):
    """Response confirming interaction event logged."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    interaction_type: str
    created_at: datetime


class RatingBreakdown(BaseModel):
    """Count of reviews per star rating tier (1 to 5)."""

    one_star: int = 0
    two_star: int = 0
    three_star: int = 0
    four_star: int = 0
    five_star: int = 0


class RecentReviewItem(BaseModel):
    """Sanitized non-sensitive review summary for owner dashboard."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    overall_rating: int
    comment: Optional[str] = None
    created_at: datetime
    has_response: bool = False
    verification_level: str = "UNVERIFIED"


class RecentRedemptionItem(BaseModel):
    """Sanitized non-sensitive offer redemption summary."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    offer_id: UUID
    offer_title: str
    redeemed_at: datetime
    status: str


class BusinessAnalyticsResponse(BaseModel):
    """Comprehensive performance analytics for a single business listing."""

    model_config = ConfigDict(from_attributes=True)

    business_id: UUID
    business_name: str
    period_days: int
    profile_views: int
    direction_requests: int
    calls: int
    offer_views: int
    offer_redemptions: int
    favorites_count: int
    total_reviews: int
    average_rating: Optional[float] = None
    rating_breakdown: RatingBreakdown
    unanswered_reviews_count: int
    active_offers_count: int
    active_services_count: int
    photos_count: int
    recent_reviews: List[RecentReviewItem] = []
    recent_redemptions: List[RecentRedemptionItem] = []


class BusinessSummaryCard(BaseModel):
    """High-level summary metrics card for an individual business."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    status: str
    verification_status: str
    average_rating: Optional[float] = None
    review_count: int = 0
    profile_views: int = 0
    direction_requests: int = 0
    calls: int = 0
    offer_redemptions: int = 0
    active_offers_count: int = 0


class OwnerDashboardResponse(BaseModel):
    """Consolidated KPI overview across all listings belonging to a business owner."""

    owner_id: UUID
    total_businesses: int
    total_profile_views: int
    total_direction_requests: int
    total_calls: int
    total_reviews: int
    average_rating: Optional[float] = None
    total_offer_redemptions: int
    unread_notifications_count: int
    businesses: List[BusinessSummaryCard] = []
