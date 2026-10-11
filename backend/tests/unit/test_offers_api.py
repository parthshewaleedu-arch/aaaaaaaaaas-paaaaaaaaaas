"""Unit tests for Offer API endpoints."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.main import app
from app.models.offer import Offer, OfferDiscountType, OfferStatus
from app.models.offer_redemption import OfferRedemption, OfferRedemptionStatus
from app.models.user import User, UserRole, UserStatus
from app.schemas.offer import OfferRedemptionValidateResponse
from app.services.offer_service import OfferService


def _dummy_offer(business_id=None, offer_id=None, title="Student Special"):
    b_id = business_id or uuid4()
    o_id = offer_id or uuid4()
    now = datetime.now(timezone.utc)
    return Offer(
        id=o_id,
        business_id=b_id,
        title=title,
        description="Get discount on meals",
        discount_type=OfferDiscountType.PERCENTAGE,
        discount_value=15.0,
        terms_conditions="Valid with student ID",
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=30),
        max_redemptions=100,
        redemption_count=5,
        status=OfferStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )


def test_list_offers_endpoint():
    """Test public GET /api/v1/offers."""
    mock_db = MagicMock()
    offer = _dummy_offer()

    original_list = OfferService.list_offers
    OfferService.list_offers = staticmethod(lambda **kwargs: ([offer], 1))

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get("/api/v1/offers")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Student Special"
        assert data["items"][0]["discount_value"] == 15.0
    finally:
        OfferService.list_offers = original_list
        app.dependency_overrides.clear()


def test_get_offer_details_endpoint():
    """Test public GET /api/v1/offers/{id}."""
    mock_db = MagicMock()
    offer = _dummy_offer()

    original_get = OfferService.get_offer
    OfferService.get_offer = staticmethod(lambda offer_id, db: offer)

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/offers/{offer.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(offer.id)
        assert data["title"] == "Student Special"
    finally:
        OfferService.get_offer = original_get
        app.dependency_overrides.clear()


def test_create_business_offer_endpoint():
    """Test authenticated POST /api/v1/businesses/{id}/offers."""
    mock_db = MagicMock()
    business_id = uuid4()
    owner_id = uuid4()
    owner = User(id=owner_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)
    created_offer = _dummy_offer(business_id=business_id)

    original_create = OfferService.create_offer
    OfferService.create_offer = staticmethod(lambda *args, **kwargs: created_offer)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        now = datetime.now(timezone.utc)
        payload = {
            "title": "Student Special",
            "description": "Get discount on meals",
            "discount_type": "PERCENTAGE",
            "discount_value": 15.0,
            "terms_conditions": "Valid with student ID",
            "valid_from": now.isoformat(),
            "valid_until": (now + timedelta(days=30)).isoformat(),
            "max_redemptions": 100,
        }
        response = client.post(
            f"/api/v1/businesses/{business_id}/offers",
            json=payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Student Special"
        assert data["discount_value"] == 15.0
    finally:
        OfferService.create_offer = original_create
        app.dependency_overrides.clear()


def test_list_business_offers_endpoint():
    """Test GET /api/v1/businesses/{id}/offers."""
    mock_db = MagicMock()
    business_id = uuid4()
    offer = _dummy_offer(business_id=business_id)

    original_list = OfferService.list_business_offers
    OfferService.list_business_offers = staticmethod(
        lambda *args, **kwargs: ([offer], 1)
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{business_id}/offers")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
    finally:
        OfferService.list_business_offers = original_list
        app.dependency_overrides.clear()


def test_update_offer_endpoint():
    """Test PATCH /api/v1/offers/{id}."""
    mock_db = MagicMock()
    offer_id = uuid4()
    owner = User(id=uuid4(), role=UserRole.OWNER, status=UserStatus.ACTIVE)
    updated_offer = _dummy_offer(offer_id=offer_id, title="Updated Title")

    original_update = OfferService.update_offer
    OfferService.update_offer = staticmethod(lambda *args, **kwargs: updated_offer)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        response = client.patch(
            f"/api/v1/offers/{offer_id}",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
    finally:
        OfferService.update_offer = original_update
        app.dependency_overrides.clear()


def test_cancel_offer_endpoint():
    """Test DELETE /api/v1/offers/{id}."""
    mock_db = MagicMock()
    offer_id = uuid4()
    owner = User(id=uuid4(), role=UserRole.OWNER, status=UserStatus.ACTIVE)
    cancelled_offer = _dummy_offer(offer_id=offer_id)
    cancelled_offer.status = OfferStatus.CANCELLED

    original_cancel = OfferService.delete_or_cancel_offer
    OfferService.delete_or_cancel_offer = staticmethod(
        lambda *args, **kwargs: cancelled_offer
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        response = client.delete(f"/api/v1/offers/{offer_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CANCELLED"
    finally:
        OfferService.delete_or_cancel_offer = original_cancel
        app.dependency_overrides.clear()


def test_redeem_offer_endpoint():
    """Test authenticated POST /api/v1/offers/{id}/redeem."""
    mock_db = MagicMock()
    offer_id = uuid4()
    student_id = uuid4()
    student = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)

    now = datetime.now(timezone.utc)
    redemption = OfferRedemption(
        id=uuid4(),
        offer_id=offer_id,
        user_id=student_id,
        redeemed_at=now,
        status=OfferRedemptionStatus.PENDING,
        verification_code="OFR-STUDENT1",
        expires_at=now + timedelta(hours=2),
    )

    original_redeem = OfferService.redeem_offer
    OfferService.redeem_offer = staticmethod(lambda *args, **kwargs: redemption)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: student
    try:
        client = TestClient(app)
        response = client.post(f"/api/v1/offers/{offer_id}/redeem")
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["verification_code"] == "OFR-STUDENT1"
        assert data["status"] == "PENDING"
    finally:
        OfferService.redeem_offer = original_redeem
        app.dependency_overrides.clear()


def test_get_my_redemptions_endpoint():
    """Test authenticated GET /api/v1/offers/my-redemptions."""
    mock_db = MagicMock()
    student_id = uuid4()
    student = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)

    now = datetime.now(timezone.utc)
    redemption = OfferRedemption(
        id=uuid4(),
        offer_id=uuid4(),
        user_id=student_id,
        redeemed_at=now,
        status=OfferRedemptionStatus.PENDING,
        verification_code="OFR-MYCODE",
        expires_at=now + timedelta(hours=2),
    )

    original_list_user = OfferService.list_user_redemptions
    OfferService.list_user_redemptions = staticmethod(
        lambda *args, **kwargs: ([redemption], 1)
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: student
    try:
        client = TestClient(app)
        response = client.get("/api/v1/offers/my-redemptions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["verification_code"] == "OFR-MYCODE"
    finally:
        OfferService.list_user_redemptions = original_list_user
        app.dependency_overrides.clear()


def test_validate_redemption_endpoint():
    """Test merchant POST /api/v1/businesses/{id}/offers/validate."""
    mock_db = MagicMock()
    business_id = uuid4()
    owner = User(id=uuid4(), role=UserRole.OWNER, status=UserStatus.ACTIVE)

    val_resp = OfferRedemptionValidateResponse(
        success=True,
        message="Redemption successfully validated and completed.",
        redemption_id=uuid4(),
        offer_id=uuid4(),
        offer_title="Student Special",
        discount_type=OfferDiscountType.PERCENTAGE,
        discount_value=15.0,
        student_id=uuid4(),
        student_display_name="Verified Student",
        status=OfferRedemptionStatus.COMPLETED,
    )

    original_validate = OfferService.validate_redemption
    OfferService.validate_redemption = staticmethod(lambda *args, **kwargs: val_resp)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        response = client.post(
            f"/api/v1/businesses/{business_id}/offers/validate",
            json={"verification_code": "OFR-VAL123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "COMPLETED"
        assert data["discount_value"] == 15.0
    finally:
        OfferService.validate_redemption = original_validate
        app.dependency_overrides.clear()
