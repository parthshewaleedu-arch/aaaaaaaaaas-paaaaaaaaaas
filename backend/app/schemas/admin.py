"""Admin Schemas.

Validation and serialization schemas for administrator dashboard metrics,
user management, business approval/status changes, review moderation, and audit logs.
"""

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.business import BusinessStatus, BusinessVerificationStatus
from app.models.user import UserRole, UserStatus


# -------------------------------------------------------------------------
# Dashboard Metrics
# -------------------------------------------------------------------------
class AdminStudentMetrics(BaseModel):
    """Student count metrics."""

    total: int
    verified: int
    pending_verification: int


class AdminBusinessMetrics(BaseModel):
    """Business listing count metrics."""

    total: int
    active: int
    pending_verification: int
    verified: int


class AdminReviewMetrics(BaseModel):
    """Review activity metrics."""

    total: int
    this_month: int


class AdminReportMetrics(BaseModel):
    """Pending moderation report metrics."""

    pending_review_reports: int
    pending_business_reports: int


class AdminDashboardData(BaseModel):
    """Aggregated administration dashboard payload."""

    students: AdminStudentMetrics
    businesses: AdminBusinessMetrics
    reviews: AdminReviewMetrics
    reports: AdminReportMetrics


class AdminDashboardResponse(BaseModel):
    """Response envelope for admin dashboard metrics."""

    success: bool = True
    data: AdminDashboardData


# -------------------------------------------------------------------------
# User Management
# -------------------------------------------------------------------------
class AdminUserItemResponse(BaseModel):
    """User profile item for admin user directory."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    phone: Optional[str] = None
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    is_phone_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class AdminUserListResponse(BaseModel):
    """Paginated list response for users."""

    success: bool = True
    data: List[AdminUserItemResponse]
    total: int
    page: int
    limit: int


class AdminUserStatusUpdateRequest(BaseModel):
    """Schema for updating user lifecycle state (suspend, activate)."""

    status: UserStatus
    reason: Optional[str] = Field(None, max_length=1000)


# -------------------------------------------------------------------------
# Business Management
# -------------------------------------------------------------------------
class AdminBusinessItemResponse(BaseModel):
    """Business summary representation for administrative oversight."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    owner_id: UUID
    owner_email: Optional[str] = None
    campus_id: Optional[UUID] = None
    campus_name: Optional[str] = None
    status: BusinessStatus
    verification_status: BusinessVerificationStatus
    average_rating: Optional[float] = None
    review_count: int = 0
    created_at: datetime
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None


class AdminBusinessListResponse(BaseModel):
    """Paginated list response for businesses under admin review."""

    success: bool = True
    data: List[AdminBusinessItemResponse]
    total: int
    page: int
    limit: int


class AdminBusinessVerifyRequest(BaseModel):
    """Schema for approving or rejecting business verification."""

    action: str = Field(
        ...,
        pattern=r"^(APPROVE|REJECT)$",
        description="Action: APPROVE or REJECT",
    )
    reason: Optional[str] = Field(None, max_length=1000)


class AdminBusinessStatusUpdateRequest(BaseModel):
    """Schema for updating business lifecycle status."""

    status: BusinessStatus
    reason: Optional[str] = Field(None, max_length=1000)


# -------------------------------------------------------------------------
# Review Moderation
# -------------------------------------------------------------------------
class AdminReviewItemResponse(BaseModel):
    """Review item representation in admin moderation queue."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    business_name: Optional[str] = None
    user_id: UUID
    user_email: Optional[str] = None
    overall_rating: float
    review_text: Optional[str] = None
    verification_level: str
    status: str
    helpful_count: int = 0
    report_count: int = 0
    created_at: datetime
    deleted_at: Optional[datetime] = None


class AdminReviewListResponse(BaseModel):
    """Paginated list response for reviews moderation queue."""

    success: bool = True
    data: List[AdminReviewItemResponse]
    total: int
    page: int
    limit: int


class AdminReviewModerateRequest(BaseModel):
    """Schema for moderating a review."""

    action: str = Field(
        ...,
        pattern=r"^(KEEP|REMOVE)$",
        description="Action: KEEP or REMOVE",
    )
    reason: Optional[str] = Field(None, max_length=1000)


# -------------------------------------------------------------------------
# Audit Logs
# -------------------------------------------------------------------------
class AdminAuditLogAdminInfo(BaseModel):
    """Basic admin identity inside audit log record."""

    id: UUID
    email: str


class AdminAuditLogItemResponse(BaseModel):
    """Single audit trail record."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    admin: Optional[AdminAuditLogAdminInfo] = None
    action: str
    entity_type: str
    entity_id: UUID
    old_data: Optional[Any] = None
    new_data: Optional[Any] = None
    reason: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class AdminAuditLogListResponse(BaseModel):
    """Paginated audit logs response."""

    success: bool = True
    data: List[AdminAuditLogItemResponse]
    total: int
    page: int
    limit: int
