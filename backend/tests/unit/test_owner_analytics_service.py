"""Unit tests for OwnerAnalyticsService."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.business import Business, BusinessStatus, BusinessVerificationStatus
from app.models.business_interaction import BusinessInteraction
from app.models.business_photo import BusinessPhoto
from app.models.favorite import Favorite
from app.models.notification import Notification
from app.models.offer import Offer
from app.models.offer_redemption import OfferRedemption, OfferRedemptionStatus
from app.models.review import Review, ReviewStatus, VerificationLevel
from app.models.service import Service
from app.services.owner_analytics_service import OwnerAnalyticsService


def test_record_interaction_success():
    """Test recording an interaction event on a business profile."""
    mock_db = MagicMock()
    biz_id = uuid4()
    user_id = uuid4()

    biz = Business(id=biz_id, name="Campus Cafe", deleted_at=None)
    mock_db.query.return_value.filter.return_value.first.return_value = biz

    res = OwnerAnalyticsService.record_interaction(
        db=mock_db,
        business_id=biz_id,
        interaction_type="PROFILE_VIEW",
        user_id=user_id,
    )

    assert res.business_id == biz_id
    assert res.interaction_type == "PROFILE_VIEW"
    assert mock_db.add.called


def test_record_interaction_not_found():
    """Test recording an interaction on a nonexistent business raises 404."""
    mock_db = MagicMock()
    biz_id = uuid4()

    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        OwnerAnalyticsService.record_interaction(
            db=mock_db,
            business_id=biz_id,
            interaction_type="CALL_CLICK",
        )
    assert exc_info.value.status_code == 404


def test_get_business_analytics_metrics_and_breakdown():
    """Test aggregation of interactions, reviews, ratings breakdown, and offers."""
    mock_db = MagicMock()
    biz_id = uuid4()
    owner_id = uuid4()

    biz = Business(
        id=biz_id,
        name="Study Hub Stationery",
        owner_id=owner_id,
        average_rating=4.5,
        review_count=2,
        deleted_at=None,
    )

    r1 = Review(
        id=uuid4(),
        business_id=biz_id,
        overall_rating=5,
        review_text="Excellent service!",
        verification_level=VerificationLevel.VERIFIED_STUDENT,
        status=ReviewStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
    )
    r1.response = None  # Unanswered

    r2 = Review(
        id=uuid4(),
        business_id=biz_id,
        overall_rating=4,
        review_text="Good print quality.",
        verification_level=VerificationLevel.UNVERIFIED,
        status=ReviewStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
    )
    r2.response = MagicMock()  # Answered

    off = Offer(id=uuid4(), title="10% Off Xerox")
    red = OfferRedemption(
        id=uuid4(),
        offer_id=off.id,
        status=OfferRedemptionStatus.COMPLETED,
        redeemed_at=datetime.now(timezone.utc),
    )
    red.offer = off

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = biz
        elif model is BusinessInteraction:
            m.filter.return_value.filter.return_value.count.return_value = 15
        elif model is Favorite:
            m.filter.return_value.count.return_value = 8
        elif model is Offer:
            m.filter.return_value.count.return_value = 2
        elif model is OfferRedemption:
            m.join.return_value.filter.return_value.count.return_value = 5
            m.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
                red
            ]
        elif model is Review:
            m.filter.return_value.all.return_value = [r1, r2]
            m.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
                r1,
                r2,
            ]
        elif model is Service:
            m.filter.return_value.count.return_value = 4
        elif model is BusinessPhoto:
            m.filter.return_value.count.return_value = 3
        return m

    mock_db.query.side_effect = query_side_effect

    analytics = OwnerAnalyticsService.get_business_analytics(
        db=mock_db,
        business_id=biz_id,
        days=30,
    )

    assert analytics.business_id == biz_id
    assert analytics.business_name == "Study Hub Stationery"
    assert analytics.period_days == 30
    assert analytics.profile_views == 15
    assert analytics.favorites_count == 8
    assert analytics.total_reviews == 2
    assert analytics.average_rating == 4.5
    assert analytics.rating_breakdown.five_star == 1
    assert analytics.rating_breakdown.four_star == 1
    assert analytics.unanswered_reviews_count == 1
    assert analytics.offer_redemptions == 5
    assert analytics.active_offers_count == 2
    assert analytics.active_services_count == 4
    assert analytics.photos_count == 3
    assert len(analytics.recent_reviews) == 2
    assert len(analytics.recent_redemptions) == 1


def test_get_owner_dashboard_multiple_businesses():
    """Test owner dashboard aggregating across multiple business listings."""
    mock_db = MagicMock()
    owner_id = uuid4()
    biz1_id = uuid4()
    biz2_id = uuid4()

    biz1 = Business(
        id=biz1_id,
        name="Campus Xerox",
        owner_id=owner_id,
        status=BusinessStatus.ACTIVE,
        verification_status=BusinessVerificationStatus.VERIFIED,
        average_rating=4.0,
        review_count=10,
        deleted_at=None,
    )
    biz2 = Business(
        id=biz2_id,
        name="Campus Bakery",
        owner_id=owner_id,
        status=BusinessStatus.ACTIVE,
        verification_status=BusinessVerificationStatus.VERIFIED,
        average_rating=5.0,
        review_count=10,
        deleted_at=None,
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.all.return_value = [biz1, biz2]
        elif model is BusinessInteraction:
            m.filter.return_value.count.return_value = 20
        elif model is OfferRedemption:
            m.join.return_value.filter.return_value.count.return_value = 4
        elif model is Offer:
            m.filter.return_value.count.return_value = 1
        elif model is Notification:
            m.filter.return_value.count.return_value = 3
        return m

    mock_db.query.side_effect = query_side_effect

    dashboard = OwnerAnalyticsService.get_owner_dashboard(
        db=mock_db,
        owner_id=owner_id,
    )

    assert dashboard.owner_id == owner_id
    assert dashboard.total_businesses == 2
    assert len(dashboard.businesses) == 2
    assert dashboard.total_reviews == 20
    # Weighted average: (4.0*10 + 5.0*10) / 20 = 4.5
    assert dashboard.average_rating == 4.5
    assert dashboard.unread_notifications_count == 3
