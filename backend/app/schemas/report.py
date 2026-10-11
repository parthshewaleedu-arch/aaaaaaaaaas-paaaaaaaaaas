"""Report Schemas.

Validation and serialization schemas for business reports and unified admin moderation queues.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.business_report import BusinessReportReason, BusinessReportStatus


class BusinessReportCreate(BaseModel):
    """Schema for submitting a moderation report against a business listing."""

    reason: BusinessReportReason = Field(
        ...,
        description="Reason code: FAKE_LISTING, INCORRECT_INFORMATION, CLOSED_BUSINESS, "
        "INCORRECT_PRICES, FRAUD, HARASSMENT, OTHER",
    )
    description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Detailed description supporting the report",
    )


class BusinessReportResponse(BaseModel):
    """Schema for business moderation report response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    business_name: Optional[str] = None
    reported_by: UUID
    reason: str
    description: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None
    resolution_notes: Optional[str] = None


class AdminReportItemResponse(BaseModel):
    """Unified schema representing either a business or a review moderation report."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_type: str  # "BUSINESS" or "REVIEW"
    target_id: UUID  # business_id or review_id
    target_title: Optional[str] = None
    reported_by: UUID
    reporter_email: Optional[str] = None
    reason: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None
    resolution_notes: Optional[str] = None


class AdminReportListResponse(BaseModel):
    """Paginated list of unified moderation reports for admin review."""

    success: bool = True
    data: List[AdminReportItemResponse]
    total: int
    page: int
    limit: int


class ReportResolveRequest(BaseModel):
    """Schema for resolving or dismissing a moderation report."""

    status: BusinessReportStatus = Field(
        default=BusinessReportStatus.RESOLVED,
        description="Target status (RESOLVED, DISMISSED, UNDER_REVIEW)",
    )
    resolution_notes: Optional[str] = Field(
        None, max_length=2000, description="Notes documenting administrative resolution"
    )
