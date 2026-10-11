"""Unit tests for Photos and Favorites API endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.main import app
from app.models.business_photo import (
    BusinessPhoto,
    BusinessPhotoStatus,
    BusinessPhotoUploaderType,
)
from app.models.favorite import Favorite
from app.models.user import User, UserRole, UserStatus
from app.schemas.favorite import FavoriteItemResponse
from app.services.business_photo_service import BusinessPhotoService
from app.services.favorite_service import FavoriteService


def test_get_business_photos_endpoint():
    """Test public GET /api/v1/businesses/{id}/photos."""
    business_id = uuid4()
    mock_db = MagicMock()

    photo = BusinessPhoto(
        id=uuid4(),
        business_id=business_id,
        uploaded_by=uuid4(),
        image_url="https://images.campus.edu/cafe1.jpg",
        caption="Main counter",
        is_primary=True,
        uploader_type=BusinessPhotoUploaderType.OWNER,
        status=BusinessPhotoStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
    )

    original_list = BusinessPhotoService.list_photos
    BusinessPhotoService.list_photos = staticmethod(lambda b_id, db: ([photo], 1))

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{business_id}/photos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["image_url"] == "https://images.campus.edu/cafe1.jpg"
        assert data[0]["is_primary"] is True
    finally:
        BusinessPhotoService.list_photos = original_list
        app.dependency_overrides.clear()


def test_upload_business_photo_endpoint():
    """Test authenticated POST /api/v1/businesses/{id}/photos."""
    business_id = uuid4()
    user_id = uuid4()
    mock_db = MagicMock()

    user = User(id=user_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    created_photo = BusinessPhoto(
        id=uuid4(),
        business_id=business_id,
        uploaded_by=user_id,
        image_url="https://images.campus.edu/cafe_student.jpg",
        caption="My study corner",
        is_primary=False,
        uploader_type=BusinessPhotoUploaderType.STUDENT,
        status=BusinessPhotoStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
    )

    original_upload = BusinessPhotoService.upload_photo
    BusinessPhotoService.upload_photo = staticmethod(
        lambda *args, **kwargs: created_photo
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        payload = {
            "image_url": "https://images.campus.edu/cafe_student.jpg",
            "caption": "My study corner",
            "is_primary": False,
        }
        response = client.post(f"/api/v1/businesses/{business_id}/photos", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["image_url"] == "https://images.campus.edu/cafe_student.jpg"
        assert data["caption"] == "My study corner"
    finally:
        BusinessPhotoService.upload_photo = original_upload
        app.dependency_overrides.clear()


def test_set_primary_business_photo_endpoint():
    """Test PATCH /api/v1/businesses/{id}/photos/{photo_id}/primary."""
    business_id = uuid4()
    photo_id = uuid4()
    owner_id = uuid4()
    mock_db = MagicMock()

    owner = User(id=owner_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)
    updated_photo = BusinessPhoto(
        id=photo_id,
        business_id=business_id,
        uploaded_by=owner_id,
        image_url="https://images.campus.edu/new_primary.jpg",
        is_primary=True,
        uploader_type=BusinessPhotoUploaderType.OWNER,
        status=BusinessPhotoStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
    )

    original_set_primary = BusinessPhotoService.set_primary_photo
    BusinessPhotoService.set_primary_photo = staticmethod(
        lambda *args, **kwargs: updated_photo
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner
    try:
        client = TestClient(app)
        response = client.patch(
            f"/api/v1/businesses/{business_id}/photos/{photo_id}/primary"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_primary"] is True
    finally:
        BusinessPhotoService.set_primary_photo = original_set_primary
        app.dependency_overrides.clear()


def test_delete_business_photo_endpoint():
    """Test DELETE /api/v1/businesses/{id}/photos/{photo_id}."""
    business_id = uuid4()
    photo_id = uuid4()
    user_id = uuid4()
    mock_db = MagicMock()

    user = User(id=user_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)

    original_delete = BusinessPhotoService.delete_photo
    BusinessPhotoService.delete_photo = staticmethod(lambda *args, **kwargs: True)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.delete(f"/api/v1/businesses/{business_id}/photos/{photo_id}")
        assert response.status_code == 204
    finally:
        BusinessPhotoService.delete_photo = original_delete
        app.dependency_overrides.clear()


def test_get_my_favorites_endpoint():
    """Test authenticated GET /api/v1/students/me/favorites."""
    student_id = uuid4()
    business_id = uuid4()
    mock_db = MagicMock()

    user = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    fav_item = FavoriteItemResponse(
        business_id=business_id,
        business_name="Campus Mess",
        category_name="Mess & Dining",
        rating=4.5,
        review_count=18,
        primary_photo_url="https://images.campus.edu/mess.jpg",
        price_level="₹",
        student_discount=True,
        is_open_now=True,
        current_status="Open now",
        distance_meters=250,
        saved_at=datetime.now(timezone.utc),
    )

    original_list_fav = FavoriteService.list_user_favorites
    FavoriteService.list_user_favorites = staticmethod(
        lambda *args, **kwargs: ([fav_item], 1)
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.get("/api/v1/students/me/favorites")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["business_name"] == "Campus Mess"
        assert data["items"][0]["rating"] == 4.5
    finally:
        FavoriteService.list_user_favorites = original_list_fav
        app.dependency_overrides.clear()


def test_add_business_to_favorites_endpoint():
    """Test authenticated POST /api/v1/students/me/favorites/{business_id}."""
    student_id = uuid4()
    business_id = uuid4()
    mock_db = MagicMock()

    user = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    fav = Favorite(user_id=student_id, business_id=business_id)

    original_add = FavoriteService.add_favorite
    FavoriteService.add_favorite = staticmethod(lambda *args, **kwargs: fav)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.post(f"/api/v1/students/me/favorites/{business_id}")
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["is_favorite"] is True
    finally:
        FavoriteService.add_favorite = original_add
        app.dependency_overrides.clear()


def test_remove_business_from_favorites_endpoint():
    """Test authenticated DELETE /api/v1/students/me/favorites/{business_id}."""
    student_id = uuid4()
    business_id = uuid4()
    mock_db = MagicMock()

    user = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)

    original_remove = FavoriteService.remove_favorite
    FavoriteService.remove_favorite = staticmethod(lambda *args, **kwargs: True)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.delete(f"/api/v1/students/me/favorites/{business_id}")
        assert response.status_code == 204
    finally:
        FavoriteService.remove_favorite = original_remove
        app.dependency_overrides.clear()


def test_check_business_is_favorite_endpoint():
    """Test GET /api/v1/businesses/{id}/is-favorite."""
    user_id = uuid4()
    business_id = uuid4()
    mock_db = MagicMock()

    user = User(id=user_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)

    original_is_fav = FavoriteService.is_favorite
    FavoriteService.is_favorite = staticmethod(lambda *args, **kwargs: True)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{business_id}/is-favorite")
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] is True
    finally:
        FavoriteService.is_favorite = original_is_fav
        app.dependency_overrides.clear()


def test_toggle_business_favorite_endpoint():
    """Test POST /api/v1/businesses/{id}/favorite."""
    user_id = uuid4()
    business_id = uuid4()
    mock_db = MagicMock()

    user = User(id=user_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)

    original_toggle = FavoriteService.toggle_favorite
    FavoriteService.toggle_favorite = staticmethod(
        lambda *args, **kwargs: (True, "Business added to favorites")
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.post(f"/api/v1/businesses/{business_id}/favorite")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_favorite"] is True
    finally:
        FavoriteService.toggle_favorite = original_toggle
        app.dependency_overrides.clear()
