"""Notification Endpoints.

Allows users to retrieve, view, and acknowledge in-app alerts and notifications.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationMarkReadResponse,
    NotificationReadAllResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List user notifications",
)
def list_notifications(
    skip: int = Query(0, ge=0, description="Offset items"),
    limit: int = Query(20, ge=1, le=100, description="Page limit"),
    unread_only: bool = Query(False, description="Filter for unread alerts only"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieve notifications belonging to the authenticated user."""
    items, total, unread_count = NotificationService.list_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in items],
        total=total,
        unread_count=unread_count,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/unread-count",
    response_model=NotificationUnreadCountResponse,
    summary="Get unread notifications count",
)
def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the total count of unread notifications for badge counters."""
    unread_count = NotificationService.get_unread_count(
        db=db,
        user_id=current_user.id,
    )
    return NotificationUnreadCountResponse(unread_count=unread_count)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationMarkReadResponse,
    summary="Mark a notification as read",
)
def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Acknowledge and mark a single notification as read."""
    notification = NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return NotificationMarkReadResponse(
        id=notification.id,
        is_read=notification.is_read,
        read_at=notification.read_at,
    )


@router.post(
    "/read-all",
    response_model=NotificationReadAllResponse,
    summary="Mark all notifications as read",
)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark all unread notifications for authenticated user as read."""
    marked_count = NotificationService.mark_all_as_read(
        db=db,
        user_id=current_user.id,
    )
    return NotificationReadAllResponse(
        marked_count=marked_count,
        message=f"Marked {marked_count} notifications as read",
    )
