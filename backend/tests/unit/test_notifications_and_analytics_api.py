"""Unit tests for Notifications and Owner Analytics REST API endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import (
    get_current_active_user,
    get_current_owner_user,
    get_optional_current_user,
)
from app.core.database import get_db
from app.main import app
from app.models.business import Business, BusinessStatus, BusinessVerificationStatus
from app.models.notification import Notification
from app.models.user import User, UserRole, UserStatus
from app.schemas.owner_analytics import (
    BusinessAnalyticsResponse,
    BusinessInteractionResponse,
    BusinessSummaryCard,
    OwnerDashboardResponse,
    RatingBreakdown,
)
from app.services.business_service import BusinessService
from app.services.notification_service import NotificationService
from app.services.owner_analytics_service import OwnerAnalyticsService


def test_get_notifications_endpoint(monkeypatch):
    """Test GET /api/v1/notifications returns user's notification list."""
    mock_db = MagicMock()
    user_id = uuid4()
    mock_user = User(
        id=user_id,
        email="student@college.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    notif = Notification(
        id=uuid4(),
        user_id=user_id,
        title="New Review Received",
        body="A student left a 5-star review.",
        type="NEW_REVIEW",
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        NotificationService,
        "list_user_notifications",
        classmethod(lambda cls, *args, **kwargs: ([notif], 1, 1)),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        client = TestClient(app)
        response = client.get("/api/v1/notifications?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["unread_count"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "New Review Received"
    finally:
        app.dependency_overrides.clear()


def test_get_notifications_unread_count_endpoint(monkeypatch):
    """Test GET /api/v1/notifications/unread-count returns integer count."""
    mock_db = MagicMock()
    mock_user = User(
        id=uuid4(),
        email="owner@business.com",
        role=UserRole.OWNER,
        status=UserStatus.ACTIVE,
    )

    monkeypatch.setattr(
        NotificationService,
        "get_unread_count",
        classmethod(lambda cls, *args, **kwargs: 4),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        client = TestClient(app)
        response = client.get("/api/v1/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 4
    finally:
        app.dependency_overrides.clear()


def test_mark_notification_read_endpoint_success(monkeypatch):
    """Test PATCH /api/v1/notifications/{id}/read marks notification as read."""
    mock_db = MagicMock()
    user_id = uuid4()
    notif_id = uuid4()
    mock_user = User(
        id=user_id,
        email="user@univ.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    notif = Notification(
        id=notif_id,
        user_id=user_id,
        title="System Notice",
        body="Maintenance alert",
        type="SYSTEM",
        is_read=True,
        read_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        NotificationService,
        "mark_as_read",
        classmethod(lambda cls, *args, **kwargs: notif),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        client = TestClient(app)
        response = client.patch(f"/api/v1/notifications/{notif_id}/read")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(notif_id)
        assert data["is_read"] is True
        assert data["read_at"] is not None
    finally:
        app.dependency_overrides.clear()


def test_mark_notification_read_endpoint_not_found(monkeypatch):
    """Test PATCH /api/v1/notifications/{id}/read returns 404 if notification doesn't exist."""
    mock_db = MagicMock()
    mock_user = User(
        id=uuid4(),
        email="user@univ.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    monkeypatch.setattr(
        NotificationService,
        "mark_as_read",
        classmethod(lambda cls, *args, **kwargs: None),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        client = TestClient(app)
        notif_id = uuid4()
        response = client.patch(f"/api/v1/notifications/{notif_id}/read")
        assert response.status_code == 404
        data = response.json()
        assert (
            data.get("error", {}).get("code") == "RESOURCE_NOT_FOUND"
            or "detail" in data
        )
    finally:
        app.dependency_overrides.clear()


def test_mark_all_notifications_read_endpoint(monkeypatch):
    """Test POST /api/v1/notifications/read-all marks all unread notifications."""
    mock_db = MagicMock()
    mock_user = User(
        id=uuid4(),
        email="user@univ.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    monkeypatch.setattr(
        NotificationService,
        "mark_all_as_read",
        classmethod(lambda cls, *args, **kwargs: 3),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        client = TestClient(app)
        response = client.post("/api/v1/notifications/read-all")
        assert response.status_code == 200
        data = response.json()
        assert data["marked_count"] == 3
        assert "Marked 3 notifications as read" in data["message"]
    finally:
        app.dependency_overrides.clear()


def test_record_business_interaction_endpoint(monkeypatch):
    """Test POST /api/v1/businesses/{id}/interactions logs engagement signals."""
    mock_db = MagicMock()
    biz_id = uuid4()
    mock_user = User(
        id=uuid4(),
        email="visitor@univ.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    interaction_resp = BusinessInteractionResponse(
        id=uuid4(),
        business_id=biz_id,
        interaction_type="PROFILE_VIEW",
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        OwnerAnalyticsService,
        "record_interaction",
        classmethod(lambda cls, *args, **kwargs: interaction_resp),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    try:
        client = TestClient(app)
        response = client.post(
            f"/api/v1/businesses/{biz_id}/interactions",
            json={"interaction_type": "PROFILE_VIEW"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["business_id"] == str(biz_id)
        assert data["interaction_type"] == "PROFILE_VIEW"
    finally:
        app.dependency_overrides.clear()


def test_get_business_analytics_endpoint_owner_success(monkeypatch):
    """Test GET /api/v1/businesses/{id}/analytics succeeds for the verified listing owner."""
    mock_db = MagicMock()
    biz_id = uuid4()
    owner_id = uuid4()

    mock_owner = User(
        id=owner_id,
        email="owner@bakery.com",
        role=UserRole.OWNER,
        status=UserStatus.ACTIVE,
    )

    biz = Business(
        id=biz_id,
        name="Fresh Bakery",
        owner_id=owner_id,
        deleted_at=None,
    )

    analytics_resp = BusinessAnalyticsResponse(
        business_id=biz_id,
        business_name="Fresh Bakery",
        period_days=30,
        profile_views=120,
        direction_requests=45,
        calls=18,
        offer_views=50,
        offer_redemptions=12,
        favorites_count=35,
        total_reviews=8,
        average_rating=4.75,
        rating_breakdown=RatingBreakdown(five_star=6, four_star=2),
        unanswered_reviews_count=1,
        active_offers_count=2,
        active_services_count=5,
        photos_count=10,
        recent_reviews=[],
        recent_redemptions=[],
    )

    monkeypatch.setattr(
        BusinessService,
        "get_business_by_id",
        classmethod(lambda cls, *args, **kwargs: biz),
    )
    monkeypatch.setattr(
        OwnerAnalyticsService,
        "get_business_analytics",
        classmethod(lambda cls, *args, **kwargs: analytics_resp),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_owner

    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{biz_id}/analytics?days=30")
        assert response.status_code == 200
        data = response.json()
        assert data["business_id"] == str(biz_id)
        assert data["profile_views"] == 120
        assert data["direction_requests"] == 45
        assert data["average_rating"] == 4.75
    finally:
        app.dependency_overrides.clear()


def test_get_business_analytics_endpoint_forbidden_for_other_user(monkeypatch):
    """Test GET /api/v1/businesses/{id}/analytics returns 403 for unauthorized users."""
    mock_db = MagicMock()
    biz_id = uuid4()
    actual_owner_id = uuid4()
    other_user_id = uuid4()

    mock_other_user = User(
        id=other_user_id,
        email="other@univ.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    biz = Business(
        id=biz_id,
        name="Fresh Bakery",
        owner_id=actual_owner_id,
        deleted_at=None,
    )

    monkeypatch.setattr(
        BusinessService,
        "get_business_by_id",
        classmethod(lambda cls, *args, **kwargs: biz),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_other_user

    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{biz_id}/analytics")
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_get_owner_dashboard_endpoint_success(monkeypatch):
    """Test GET /api/v1/owner/dashboard returns consolidated metrics for an owner."""
    mock_db = MagicMock()
    owner_id = uuid4()
    mock_owner = User(
        id=owner_id,
        email="owner@market.com",
        role=UserRole.OWNER,
        status=UserStatus.ACTIVE,
    )

    card = BusinessSummaryCard(
        id=uuid4(),
        name="Campus Stationery",
        status=BusinessStatus.ACTIVE.value,
        verification_status=BusinessVerificationStatus.VERIFIED.value,
        average_rating=4.5,
        review_count=12,
        profile_views=85,
        direction_requests=20,
        calls=10,
        offer_redemptions=5,
        active_offers_count=1,
    )

    dashboard_resp = OwnerDashboardResponse(
        owner_id=owner_id,
        total_businesses=1,
        total_profile_views=85,
        total_direction_requests=20,
        total_calls=10,
        total_reviews=12,
        average_rating=4.5,
        total_offer_redemptions=5,
        unread_notifications_count=2,
        businesses=[card],
    )

    monkeypatch.setattr(
        OwnerAnalyticsService,
        "get_owner_dashboard",
        classmethod(lambda cls, *args, **kwargs: dashboard_resp),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_owner_user] = lambda: mock_owner

    try:
        client = TestClient(app)
        response = client.get("/api/v1/owner/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["owner_id"] == str(owner_id)
        assert data["total_businesses"] == 1
        assert data["total_profile_views"] == 85
        assert len(data["businesses"]) == 1
        assert data["businesses"][0]["name"] == "Campus Stationery"
    finally:
        app.dependency_overrides.clear()


def test_get_owner_businesses_endpoint_success(monkeypatch):
    """Test GET /api/v1/owner/businesses returns list of business cards."""
    mock_db = MagicMock()
    owner_id = uuid4()
    mock_owner = User(
        id=owner_id,
        email="owner@market.com",
        role=UserRole.OWNER,
        status=UserStatus.ACTIVE,
    )

    card = BusinessSummaryCard(
        id=uuid4(),
        name="Campus Books",
        status=BusinessStatus.ACTIVE.value,
        verification_status=BusinessVerificationStatus.VERIFIED.value,
        average_rating=4.8,
        review_count=15,
        profile_views=150,
        direction_requests=30,
        calls=12,
        offer_redemptions=8,
        active_offers_count=2,
    )

    dashboard_resp = OwnerDashboardResponse(
        owner_id=owner_id,
        total_businesses=1,
        total_profile_views=150,
        total_direction_requests=30,
        total_calls=12,
        total_reviews=15,
        average_rating=4.8,
        total_offer_redemptions=8,
        unread_notifications_count=1,
        businesses=[card],
    )

    monkeypatch.setattr(
        OwnerAnalyticsService,
        "get_owner_dashboard",
        classmethod(lambda cls, *args, **kwargs: dashboard_resp),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_owner_user] = lambda: mock_owner

    try:
        client = TestClient(app)
        response = client.get("/api/v1/owner/businesses")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Campus Books"
    finally:
        app.dependency_overrides.clear()


def test_owner_dashboard_forbidden_for_student():
    """Test GET /api/v1/owner/dashboard returns 403 Forbidden for STUDENT role."""
    mock_db = MagicMock()
    mock_student = User(
        id=uuid4(),
        email="student@univ.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_student

    try:
        client = TestClient(app)
        response = client.get("/api/v1/owner/dashboard")
        assert response.status_code == 403
        assert "owner privileges" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
