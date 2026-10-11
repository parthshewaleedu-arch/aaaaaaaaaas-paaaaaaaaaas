"""Notification Service.

Manages transactional alerts and in-app notifications for users, business owners, and administrators.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationService:
    """Service handling notification lifecycle."""

    @classmethod
    def create_notification(
        cls,
        db: Session,
        user_id: UUID,
        title: str,
        body: str,
        type: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
    ) -> Notification:
        """Create and persist an in-app notification for a user."""
        notification = Notification(
            id=uuid4(),
            user_id=user_id,
            title=title,
            body=body,
            type=type,
            reference_type=reference_type,
            reference_id=reference_id,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notification)
        try:
            db.commit()
            db.refresh(notification)
        except Exception:
            # Fallback for environments with deferred commit/flush
            try:
                db.flush()
            except Exception:
                pass
        return notification

    @classmethod
    def list_user_notifications(
        cls,
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ) -> Tuple[List[Notification], int, int]:
        """List notifications belonging to a user, with total count and unread count."""
        base_query = db.query(Notification).filter(Notification.user_id == user_id)
        unread_count = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .count()
        )

        filter_query = base_query
        if unread_only:
            filter_query = filter_query.filter(Notification.is_read.is_(False))

        total = filter_query.count()
        items = (
            filter_query.order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total, unread_count

    @classmethod
    def get_notification(
        cls,
        db: Session,
        notification_id: UUID,
        user_id: UUID,
    ) -> Optional[Notification]:
        """Retrieve a specific notification owned by user."""
        return (
            db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

    @classmethod
    def mark_as_read(
        cls,
        db: Session,
        notification_id: UUID,
        user_id: UUID,
    ) -> Optional[Notification]:
        """Mark a single user notification as read."""
        notification = cls.get_notification(db, notification_id, user_id)
        if not notification:
            return None

        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        try:
            db.commit()
            db.refresh(notification)
        except Exception:
            try:
                db.flush()
            except Exception:
                pass
        return notification

    @classmethod
    def mark_all_as_read(
        cls,
        db: Session,
        user_id: UUID,
    ) -> int:
        """Mark all unread notifications for a user as read."""
        unread_items = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .all()
        )
        now = datetime.now(timezone.utc)
        for item in unread_items:
            item.is_read = True
            item.read_at = now

        try:
            db.commit()
        except Exception:
            try:
                db.flush()
            except Exception:
                pass
        return len(unread_items)

    @classmethod
    def get_unread_count(
        cls,
        db: Session,
        user_id: UUID,
    ) -> int:
        """Return the count of unread notifications for a user."""
        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .count()
        )
