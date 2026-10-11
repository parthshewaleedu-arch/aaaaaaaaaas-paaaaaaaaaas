"""Unit tests for NotificationService."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from app.models.notification import Notification
from app.services.notification_service import NotificationService


def test_create_notification_success():
    """Test creating an in-app notification for a user."""
    mock_db = MagicMock()
    user_id = uuid4()
    ref_id = uuid4()

    notification = NotificationService.create_notification(
        db=mock_db,
        user_id=user_id,
        title="Business Verified",
        body="Your listing has been approved by admin.",
        type="BUSINESS_VERIFIED",
        reference_type="business",
        reference_id=ref_id,
    )

    assert notification.user_id == user_id
    assert notification.title == "Business Verified"
    assert notification.body == "Your listing has been approved by admin."
    assert notification.type == "BUSINESS_VERIFIED"
    assert notification.reference_type == "business"
    assert notification.reference_id == ref_id
    assert notification.is_read is False
    assert notification.read_at is None
    assert mock_db.add.called


def test_list_user_notifications_all():
    """Test listing all notifications for a user."""
    mock_db = MagicMock()
    user_id = uuid4()

    n1 = Notification(
        id=uuid4(),
        user_id=user_id,
        title="Alert 1",
        body="Body 1",
        type="SYSTEM",
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )
    n2 = Notification(
        id=uuid4(),
        user_id=user_id,
        title="Alert 2",
        body="Body 2",
        type="NEW_REVIEW",
        is_read=True,
        created_at=datetime.now(timezone.utc),
    )

    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.count.side_effect = [1, 2]  # unread_count=1, total=2
    query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
        n1,
        n2,
    ]
    mock_db.query.return_value = query_mock

    items, total, unread_count = NotificationService.list_user_notifications(
        db=mock_db,
        user_id=user_id,
        skip=0,
        limit=10,
        unread_only=False,
    )

    assert total == 2
    assert unread_count == 1
    assert len(items) == 2
    assert items[0].title == "Alert 1"


def test_list_user_notifications_unread_only():
    """Test filtering notifications by unread status only."""
    mock_db = MagicMock()
    user_id = uuid4()

    n1 = Notification(
        id=uuid4(),
        user_id=user_id,
        title="Unread Alert",
        body="Unread Body",
        type="OFFER_REDEMPTION",
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )

    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.count.side_effect = [1, 1]
    query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
        n1
    ]
    mock_db.query.return_value = query_mock

    items, total, unread_count = NotificationService.list_user_notifications(
        db=mock_db,
        user_id=user_id,
        skip=0,
        limit=10,
        unread_only=True,
    )

    assert total == 1
    assert unread_count == 1
    assert len(items) == 1
    assert items[0].is_read is False


def test_get_notification():
    """Test retrieving a specific notification by ID and user ID."""
    mock_db = MagicMock()
    user_id = uuid4()
    notif_id = uuid4()

    n = Notification(
        id=notif_id,
        user_id=user_id,
        title="Notice",
        body="Content",
        type="SYSTEM",
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )

    mock_db.query.return_value.filter.return_value.first.return_value = n

    result = NotificationService.get_notification(
        db=mock_db,
        notification_id=notif_id,
        user_id=user_id,
    )

    assert result is not None
    assert result.id == notif_id
    assert result.user_id == user_id


def test_mark_as_read_success():
    """Test marking a notification as read updates is_read and read_at."""
    mock_db = MagicMock()
    user_id = uuid4()
    notif_id = uuid4()

    n = Notification(
        id=notif_id,
        user_id=user_id,
        title="Notice",
        body="Content",
        type="SYSTEM",
        is_read=False,
        read_at=None,
        created_at=datetime.now(timezone.utc),
    )

    mock_db.query.return_value.filter.return_value.first.return_value = n

    updated = NotificationService.mark_as_read(
        db=mock_db,
        notification_id=notif_id,
        user_id=user_id,
    )

    assert updated is not None
    assert updated.is_read is True
    assert updated.read_at is not None


def test_mark_all_as_read_success():
    """Test marking all unread notifications as read."""
    mock_db = MagicMock()
    user_id = uuid4()

    n1 = Notification(
        id=uuid4(),
        user_id=user_id,
        title="Notice 1",
        body="Content 1",
        type="SYSTEM",
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )
    n2 = Notification(
        id=uuid4(),
        user_id=user_id,
        title="Notice 2",
        body="Content 2",
        type="NEW_REVIEW",
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )

    mock_db.query.return_value.filter.return_value.all.return_value = [n1, n2]

    count = NotificationService.mark_all_as_read(
        db=mock_db,
        user_id=user_id,
    )

    assert count == 2
    assert n1.is_read is True
    assert n2.is_read is True
    assert n1.read_at is not None
    assert n2.read_at is not None


def test_get_unread_count():
    """Test calculating unread notification count."""
    mock_db = MagicMock()
    user_id = uuid4()

    mock_db.query.return_value.filter.return_value.count.return_value = 5

    count = NotificationService.get_unread_count(
        db=mock_db,
        user_id=user_id,
    )

    assert count == 5
