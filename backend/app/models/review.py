"""Review Model

Represents a review left by a student for a business with multi-dimensional ratings.
"""

import enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class VerificationLevel(str, enum.Enum):
    """Review trust and verification level."""

    UNVERIFIED = "UNVERIFIED"
    VERIFIED_STUDENT = "VERIFIED_STUDENT"
    VERIFIED_VISIT = "VERIFIED_VISIT"
    VERIFIED_TRANSACTION = "VERIFIED_TRANSACTION"


class ReviewStatus(str, enum.Enum):
    """Review moderation and lifecycle status."""

    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"
    PENDING_MODERATION = "PENDING_MODERATION"


class Review(BaseModel):
    """Review model for student evaluations of campus businesses.

    Contains overall rating, review text, trust level, helpfulness counter,
    and cascading relations to dimensional ratings and photos.
    """

    __tablename__ = "reviews"

    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    overall_rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    verification_level = Column(
        Enum(VerificationLevel, name="review_verification_level", create_type=True),
        nullable=False,
        default=VerificationLevel.UNVERIFIED,
    )
    status = Column(
        Enum(ReviewStatus, name="review_status", create_type=True),
        nullable=False,
        default=ReviewStatus.ACTIVE,
        index=True,
    )
    helpful_count = Column(Integer, nullable=False, default=0)

    # Soft deletion
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    business = relationship("Business", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    ratings = relationship(
        "ReviewRating", back_populates="review", cascade="all, delete-orphan"
    )
    photos = relationship(
        "ReviewPhoto",
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="ReviewPhoto.created_at",
    )
    response = relationship(
        "ReviewResponse",
        back_populates="review",
        uselist=False,
        cascade="all, delete-orphan",
    )
    reports = relationship(
        "ReviewReport", back_populates="review", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "overall_rating >= 1 AND overall_rating <= 5",
            name="ck_reviews_rating",
        ),
        CheckConstraint("helpful_count >= 0", name="ck_reviews_helpful_count"),
    )

    @property
    def is_verified_student(self) -> bool:
        """Return True if reviewer is verified student."""
        return self.verification_level in (
            VerificationLevel.VERIFIED_STUDENT,
            VerificationLevel.VERIFIED_VISIT,
            VerificationLevel.VERIFIED_TRANSACTION,
        )

    def __repr__(self):
        return (
            f"<Review(id={self.id}, business_id={self.business_id}, "
            f"user_id={self.user_id}, rating={self.overall_rating})>"
        )
