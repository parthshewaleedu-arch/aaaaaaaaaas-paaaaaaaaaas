"""Unit tests for services and business hours API endpoints."""

from datetime import datetime, time, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.main import app
from app.models.business import Business, BusinessStatus, BusinessVerificationStatus
from app.models.business_hours import BusinessHours
from app.models.service import Service
from app.models.service_price_history import ServicePriceHistory
from app.models.user import User, UserRole, UserStatus


def test_get_business_hours_endpoint():
    """Test public GET /api/v1/businesses/{id}/hours."""
    business_id = uuid4()
    mock_db = MagicMock()

    business = Business(
        id=business_id,
        name="Campus Xerox",
        status=BusinessStatus.ACTIVE,
        verification_status=BusinessVerificationStatus.VERIFIED,
    )

    hours = [
        BusinessHours(
            id=uuid4(),
            business_id=business_id,
            day_of_week=1,
            open_time=time(9, 0),
            close_time=time(21, 0),
            is_closed=False,
        )
    ]

    mock_db.query.return_value.filter.return_value.first.return_value = business
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
        hours
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{business_id}/hours")
        assert response.status_code == 200
        data = response.json()
        assert "is_open_now" in data
        assert "current_status" in data
        assert len(data["hours"]) == 1
        assert data["hours"][0]["day_name"] == "Monday"
    finally:
        app.dependency_overrides.clear()


def test_update_business_hours_owner_success():
    """Test PUT /api/v1/businesses/{id}/hours succeeds for business owner."""
    owner_id = uuid4()
    business_id = uuid4()
    owner = User(id=owner_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)
    business = Business(id=business_id, owner_id=owner_id, name="Campus Gym")

    mock_db = MagicMock()
    # Filter for ownership check and get business
    mock_db.query.return_value.filter.return_value.first.return_value = business

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        payload = {
            "hours": [
                {
                    "day_of_week": 1,
                    "open_time": "06:00:00",
                    "close_time": "22:00:00",
                    "is_closed": False,
                },
                {
                    "day_of_week": 0,
                    "open_time": None,
                    "close_time": None,
                    "is_closed": True,
                },
            ]
        }
        response = client.put(f"/api/v1/businesses/{business_id}/hours", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "hours" in data
        assert "is_open_now" in data
    finally:
        app.dependency_overrides.clear()


def test_get_business_services_endpoint():
    """Test public GET /api/v1/businesses/{id}/services."""
    business_id = uuid4()
    mock_db = MagicMock()

    business = Business(id=business_id, name="Campus Laundry")
    service1 = Service(
        id=uuid4(),
        business_id=business_id,
        name="Wash & Fold",
        price=50.0,
        currency="INR",
        unit="kg",
        is_active=True,
        updated_at=datetime.now(timezone.utc),
    )

    mock_db.query.return_value.filter.return_value.first.return_value = business
    mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [
        service1
    ]

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{business_id}/services")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Wash & Fold"
        assert data[0]["price"] == 50.0
        assert data[0]["days_since_update"] == 0
    finally:
        app.dependency_overrides.clear()


def test_create_service_owner_success():
    """Test POST /api/v1/businesses/{id}/services succeeds for owner."""
    owner_id = uuid4()
    business_id = uuid4()
    owner = User(id=owner_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)
    business = Business(id=business_id, owner_id=owner_id, name="Campus Mess")

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = business

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        payload = {
            "name": "Monthly Mess Pass",
            "description": "2 meals daily for 30 days",
            "price": 3000.0,
            "currency": "INR",
            "unit": "month",
        }
        response = client.post(
            f"/api/v1/businesses/{business_id}/services", json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Monthly Mess Pass"
        assert data["price"] == 3000.0
    finally:
        app.dependency_overrides.clear()


def test_get_service_detail_endpoint():
    """Test public GET /api/v1/services/{service_id}."""
    service_id = uuid4()
    mock_db = MagicMock()

    service = Service(
        id=service_id,
        business_id=uuid4(),
        name="Haircut",
        price=120.0,
        currency="INR",
        unit="person",
        is_active=True,
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.query.return_value.filter.return_value.first.return_value = service

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/services/{service_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Haircut"
        assert data["price"] == 120.0
    finally:
        app.dependency_overrides.clear()


def test_patch_service_owner_success():
    """Test PATCH /api/v1/services/{service_id} updates price."""
    owner_id = uuid4()
    business_id = uuid4()
    service_id = uuid4()

    owner = User(id=owner_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)
    service = Service(
        id=service_id,
        business_id=business_id,
        name="Lunch Thali",
        price=80.0,
        currency="INR",
        unit="plate",
        is_active=True,
        updated_at=datetime.now(timezone.utc),
    )

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = service
    mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = (
        None
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        response = client.patch(
            f"/api/v1/services/{service_id}",
            json={"price": 90.0, "description": "Includes sweet"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 90.0
    finally:
        app.dependency_overrides.clear()


def test_delete_service_owner_success():
    """Test DELETE /api/v1/services/{service_id} removes offering."""
    owner_id = uuid4()
    business_id = uuid4()
    service_id = uuid4()

    owner = User(id=owner_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)
    service = Service(
        id=service_id, business_id=business_id, name="Obsolete Item", price=50.0
    )

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = service

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        response = client.delete(f"/api/v1/services/{service_id}")
        assert response.status_code == 204
    finally:
        app.dependency_overrides.clear()


def test_get_service_price_history_endpoint():
    """Test public GET /api/v1/services/{service_id}/price-history."""
    service_id = uuid4()
    service = Service(id=service_id, name="Thali", price=100.0)

    history1 = ServicePriceHistory(
        id=uuid4(),
        service_id=service_id,
        price=100.0,
        currency="INR",
        effective_from=datetime.now(timezone.utc),
        effective_to=None,
    )

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = service
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        history1
    ]

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/services/{service_id}/price-history")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["price"] == 100.0
    finally:
        app.dependency_overrides.clear()
