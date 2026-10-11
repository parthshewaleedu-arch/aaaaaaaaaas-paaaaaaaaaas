"""Unit tests for BusinessPhotoService."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.business import Business
from app.models.business_photo import (
    BusinessPhoto,
    BusinessPhotoStatus,
    BusinessPhotoUploaderType,
)
from app.models.user import User, UserRole, UserStatus
from app.schemas.business_photo import BusinessPhotoCreate
from app.services.business_photo_service import BusinessPhotoService


def test_upload_photo_owner_success():
    """Test owner uploading photo can set is_primary=True."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()

    owner = User(id=owner_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)
    business = Business(id=business_id, owner_id=owner_id, name="Campus Cafe")

    mock_db.query.return_value.filter.return_value.first.return_value = business

    photo_data = BusinessPhotoCreate(
        image_url="https://images.campus.edu/cafe_front.jpg",
        caption="Front entrance and outdoor seating",
        is_primary=True,
    )

    photo = BusinessPhotoService.upload_photo(
        business_id=business_id,
        user=owner,
        photo_data=photo_data,
        db=mock_db,
    )

    assert photo.business_id == business_id
    assert photo.uploaded_by == owner_id
    assert photo.image_url == "https://images.campus.edu/cafe_front.jpg"
    assert photo.caption == "Front entrance and outdoor seating"
    assert photo.is_primary is True
    assert photo.uploader_type == BusinessPhotoUploaderType.OWNER
    assert photo.status == BusinessPhotoStatus.ACTIVE
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_upload_photo_student_success():
    """Test student uploading photo is tagged as STUDENT and cannot set primary."""
    mock_db = MagicMock()
    owner_id = uuid4()
    student_id = uuid4()
    business_id = uuid4()

    student = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    business = Business(id=business_id, owner_id=owner_id, name="Campus Cafe")

    mock_db.query.return_value.filter.return_value.first.return_value = business

    photo_data = BusinessPhotoCreate(
        image_url="https://images.campus.edu/student_shot.jpg",
        caption="Delicious cold coffee",
        is_primary=False,
    )

    photo = BusinessPhotoService.upload_photo(
        business_id=business_id,
        user=student,
        photo_data=photo_data,
        db=mock_db,
    )

    assert photo.uploaded_by == student_id
    assert photo.uploader_type == BusinessPhotoUploaderType.STUDENT
    assert photo.is_primary is False


def test_upload_photo_student_cannot_set_primary():
    """Test student setting is_primary=True raises PermissionError."""
    mock_db = MagicMock()
    owner_id = uuid4()
    student_id = uuid4()
    business_id = uuid4()

    student = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    business = Business(id=business_id, owner_id=owner_id, name="Campus Cafe")

    mock_db.query.return_value.filter.return_value.first.return_value = business

    photo_data = BusinessPhotoCreate(
        image_url="https://images.campus.edu/student_shot.jpg",
        is_primary=True,
    )

    with pytest.raises(
        PermissionError,
        match="Only the business owner or admin can set a primary cover photo",
    ):
        BusinessPhotoService.upload_photo(
            business_id=business_id,
            user=student,
            photo_data=photo_data,
            db=mock_db,
        )


def test_upload_photo_business_not_found():
    """Test uploading to nonexistent business raises ValueError."""
    mock_db = MagicMock()
    user = User(id=uuid4(), role=UserRole.STUDENT)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    photo_data = BusinessPhotoCreate(image_url="https://images.campus.edu/test.jpg")

    with pytest.raises(ValueError, match="Business not found"):
        BusinessPhotoService.upload_photo(
            business_id=uuid4(),
            user=user,
            photo_data=photo_data,
            db=mock_db,
        )


def test_list_photos_query():
    """Test list_photos filters by business_id and status."""
    mock_db = MagicMock()
    business_id = uuid4()
    photo = BusinessPhoto(
        id=uuid4(),
        business_id=business_id,
        uploaded_by=uuid4(),
        image_url="https://images.campus.edu/cafe.jpg",
        is_primary=True,
        status=BusinessPhotoStatus.ACTIVE,
    )

    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.count.return_value = 1
    query_mock.order_by.return_value.limit.return_value.all.return_value = [photo]
    mock_db.query.return_value = query_mock

    photos, total = BusinessPhotoService.list_photos(business_id, mock_db)
    assert total == 1
    assert len(photos) == 1
    assert photos[0].is_primary is True


def test_set_primary_photo_owner_success():
    """Test business owner setting an existing photo as primary."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()
    photo_id = uuid4()

    owner = User(id=owner_id, role=UserRole.OWNER)
    business = Business(id=business_id, owner_id=owner_id)
    photo = BusinessPhoto(
        id=photo_id,
        business_id=business_id,
        uploaded_by=owner_id,
        image_url="https://images.campus.edu/new_cover.jpg",
        is_primary=False,
        status=BusinessPhotoStatus.ACTIVE,
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is BusinessPhoto:
            m.filter.return_value.first.return_value = photo
        return m

    mock_db.query.side_effect = query_side_effect

    updated_photo = BusinessPhotoService.set_primary_photo(
        business_id=business_id,
        photo_id=photo_id,
        user=owner,
        db=mock_db,
    )

    assert updated_photo.is_primary is True
    mock_db.commit.assert_called_once()


def test_set_primary_photo_forbidden_for_non_owner():
    """Test non-owner user cannot designate primary cover photo."""
    mock_db = MagicMock()
    actual_owner_id = uuid4()
    other_user_id = uuid4()
    business_id = uuid4()
    photo_id = uuid4()

    other_user = User(id=other_user_id, role=UserRole.STUDENT)
    business = Business(id=business_id, owner_id=actual_owner_id)

    mock_db.query.return_value.filter.return_value.first.return_value = business

    with pytest.raises(
        PermissionError,
        match="Only the business owner or admin can set the primary photo",
    ):
        BusinessPhotoService.set_primary_photo(
            business_id=business_id,
            photo_id=photo_id,
            user=other_user,
            db=mock_db,
        )


def test_delete_photo_by_uploader():
    """Test uploader can delete their own photo."""
    mock_db = MagicMock()
    uploader_id = uuid4()
    business_id = uuid4()
    photo_id = uuid4()

    uploader = User(id=uploader_id, role=UserRole.STUDENT)
    business = Business(id=business_id, owner_id=uuid4())
    photo = BusinessPhoto(
        id=photo_id,
        business_id=business_id,
        uploaded_by=uploader_id,
        status=BusinessPhotoStatus.ACTIVE,
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is BusinessPhoto:
            m.filter.return_value.first.return_value = photo
        elif model is Business:
            m.filter.return_value.first.return_value = business
        return m

    mock_db.query.side_effect = query_side_effect

    success = BusinessPhotoService.delete_photo(
        business_id=business_id,
        photo_id=photo_id,
        user=uploader,
        db=mock_db,
    )

    assert success is True
    assert photo.status == BusinessPhotoStatus.REMOVED
    mock_db.commit.assert_called_once()


def test_delete_photo_by_business_owner():
    """Test business owner can delete photo uploaded by any student."""
    mock_db = MagicMock()
    owner_id = uuid4()
    business_id = uuid4()
    photo_id = uuid4()

    owner = User(id=owner_id, role=UserRole.OWNER)
    business = Business(id=business_id, owner_id=owner_id)
    photo = BusinessPhoto(
        id=photo_id,
        business_id=business_id,
        uploaded_by=uuid4(),  # Different user
        status=BusinessPhotoStatus.ACTIVE,
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is BusinessPhoto:
            m.filter.return_value.first.return_value = photo
        elif model is Business:
            m.filter.return_value.first.return_value = business
        return m

    mock_db.query.side_effect = query_side_effect

    success = BusinessPhotoService.delete_photo(
        business_id=business_id,
        photo_id=photo_id,
        user=owner,
        db=mock_db,
    )

    assert success is True
    assert photo.status == BusinessPhotoStatus.REMOVED
    mock_db.commit.assert_called_once()
