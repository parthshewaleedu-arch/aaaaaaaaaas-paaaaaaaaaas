"""Review Report Model

Represents a moderation report filed against a review.
"""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ReviewReportReason(str, enum.Enum):
    """Reason for reporting a review."""

    SPAM = "SPAM"
    FAKE_REVIEW = "FAKE_REVIEW"
    HARASSMENT = "HARASSMENT"
    PERSONAL_INFORMATION = "PERSONAL_INFORMATION"
    ABUSE = "ABUSE"
    IRRELEVANT = "IRRELEVANT"
    EXTORTION = "EXTORTION"
    OTHER = "OTHER"


class ReviewReportStatus(str, enum.Enum):
    """Review report lifecycle state."""

    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ReviewReport(BaseModel):
    """Moderation report filed against a problematic review."""

    __tablename__ = "review_reports"

    review_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
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
        Enum(ReviewReportReason, name="review_report_reason", create_type=True),
        nullable=False,
    )
    description = Column(Text, nullable=True)

    status = Column(
        Enum(ReviewReportStatus, name="review_report_status", create_type=True),
        nullable=False,
        default=ReviewReportStatus.PENDING,
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
    review = relationship("Review", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reported_by])
    resolver = relationship("User", foreign_keys=[resolved_by])

    def __repr__(self):
        return f"<ReviewReport(id={self.id}, review_id={self.review_id}, reason={self.reason}, status={self.status})>"
