"""Unit tests for categories API endpoints."""

from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.main import app
from app.models.category import Category
from app.models.user import User, UserRole, UserStatus


def test_list_categories_endpoint_flat():
    """Test public GET /api/v1/categories."""
    mock_db = MagicMock()
    cat = Category(
        id=uuid4(),
        name="Food",
        slug="food",
        description="Dining",
        parent_id=None,
        is_active=True,
        display_order=1,
    )
    q_mock = mock_db.query.return_value.filter.return_value.order_by.return_value
    q_mock.offset.return_value.limit.return_value.all.return_value = [cat]

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Food"
        assert data[0]["slug"] == "food"
    finally:
        app.dependency_overrides.clear()


def test_create_category_admin_only_forbidden_for_student():
    """Test POST /api/v1/categories forbidden for non-admin users."""
    mock_user = User(
        id=uuid4(),
        email="student@mitaoe.ac.in",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    mock_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/categories",
            json={"name": "New Category", "display_order": 1},
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_create_category_admin_success():
    """Test POST /api/v1/categories succeeds for ADMIN."""
    mock_user = User(
        id=uuid4(),
        email="admin@aaspaas.com",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/categories",
            json={
                "name": "Health",
                "description": "Medical shops and clinics",
                "icon": "local_hospital",
                "display_order": 2,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Health"
        assert data["slug"] == "health"
    finally:
        app.dependency_overrides.clear()
