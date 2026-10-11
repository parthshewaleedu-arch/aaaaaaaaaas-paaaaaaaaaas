"""Business Report Model.

Represents a report filed by a user against a business for moderation review.
"""

import enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class BusinessReportReason(str, enum.Enum):
    """Reason for reporting a business."""

    FAKE_LISTING = "FAKE_LISTING"
    INCORRECT_INFORMATION = "INCORRECT_INFORMATION"
    CLOSED_BUSINESS = "CLOSED_BUSINESS"
    INCORRECT_PRICES = "INCORRECT_PRICES"
    FRAUD = "FRAUD"
    HARASSMENT = "HARASSMENT"
    OTHER = "OTHER"


class BusinessReportStatus(str, enum.Enum):
    """Business report moderation status."""

    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class BusinessReport(BaseModel):
    """Moderation report filed against a business listing."""

    __tablename__ = "business_reports"

    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reported_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reason = Column(
        Enum(BusinessReportReason, name="business_report_reason", create_type=True),
        nullable=False,
    )
    description = Column(Text, nullable=False)

    status = Column(
        Enum(BusinessReportStatus, name="business_report_status", create_type=True),
        nullable=False,
        default=BusinessReportStatus.PENDING,
        index=True,
    )

    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    business = relationship("Business", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reported_by])
    resolver = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        CheckConstraint(
            "reason IN ('FAKE_LISTING', 'INCORRECT_INFORMATION', 'CLOSED_BUSINESS', "
            "'INCORRECT_PRICES', 'FRAUD', 'HARASSMENT', 'OTHER')",
            name="ck_business_reports_reason",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'UNDER_REVIEW', 'RESOLVED', 'DISMISSED')",
            name="ck_business_reports_status",
        ),
    )

    def __repr__(self):
        return (
            f"<BusinessReport(id={self.id}, business_id={self.business_id}, "
            f"reason={self.reason}, status={self.status})>"
        )
