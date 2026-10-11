"""Notification Schemas.

Validation and serialization schemas for user notifications.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationType(str, Enum):
    """Notification classification types."""

    SYSTEM = "SYSTEM"
    BUSINESS_VERIFIED = "BUSINESS_VERIFIED"
    BUSINESS_REJECTED = "BUSINESS_REJECTED"
    NEW_REVIEW = "NEW_REVIEW"
    REVIEW_RESPONSE = "REVIEW_RESPONSE"
    OFFER_REDEMPTION = "OFFER_REDEMPTION"
    OFFER_EXPIRING = "OFFER_EXPIRING"
    REPORT_RECEIVED = "REPORT_RECEIVED"
    REPORT_RESOLVED = "REPORT_RESOLVED"


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    user_id: UUID
    title: str = Field(..., max_length=255, description="Notification header")
    body: str = Field(..., description="Notification body content")
    type: str = Field(
        default=NotificationType.SYSTEM.value,
        max_length=50,
        description="Notification type",
    )
    reference_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Referenced entity type (e.g. business, review, offer, report)",
    )
    reference_id: Optional[UUID] = Field(
        None,
        description="Referenced entity UUID",
    )


class NotificationResponse(BaseModel):
    """Schema for notification item response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    body: str
    type: str
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    """Paginated list of user notifications."""

    items: List[NotificationResponse]
    total: int
    unread_count: int
    skip: int
    limit: int


class NotificationMarkReadResponse(BaseModel):
    """Response when marking a single notification as read."""

    id: UUID
    is_read: bool
    read_at: Optional[datetime] = None


class NotificationReadAllResponse(BaseModel):
    """Response when marking all notifications as read."""

    marked_count: int
    message: str


class NotificationUnreadCountResponse(BaseModel):
    """Response for unread notification count."""

    unread_count: int
