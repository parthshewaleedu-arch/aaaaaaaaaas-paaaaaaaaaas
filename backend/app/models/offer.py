"""Offer Model.

Defines business promotional offers, discounts, and terms.
"""

from enum import Enum as PyEnum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class OfferDiscountType(str, PyEnum):
    """Types of discounts that can be offered."""

    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    SERVICE_DISCOUNT = "SERVICE_DISCOUNT"


class OfferStatus(str, PyEnum):
    """Lifecycle status of an offer."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class Offer(BaseModel):
    """Offer model representing a discount/promotion created by a business."""

    __tablename__ = "offers"

    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    discount_type = Column(
        Enum(OfferDiscountType, name="offer_discount_type", create_type=True),
        nullable=False,
    )
    discount_value = Column(Numeric(10, 2), nullable=False)
    terms_conditions = Column(Text, nullable=True)
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False, index=True)
    max_redemptions = Column(Integer, nullable=True)
    redemption_count = Column(Integer, nullable=False, default=0)
    status = Column(
        Enum(OfferStatus, name="offer_status", create_type=True),
        nullable=False,
        default=OfferStatus.DRAFT,
        index=True,
    )

    # Relationships
    business = relationship("Business", back_populates="offers")
    redemptions = relationship(
        "OfferRedemption",
        back_populates="offer",
        cascade="all, delete-orphan",
        order_by="desc(OfferRedemption.redeemed_at)",
    )

    __table_args__ = (
        CheckConstraint("discount_value > 0", name="ck_offers_discount_value"),
        CheckConstraint(
            "max_redemptions IS NULL OR max_redemptions > 0",
            name="ck_offers_redemptions",
        ),
        CheckConstraint(
            "redemption_count >= 0",
            name="ck_offers_redemption_count",
        ),
        CheckConstraint(
            "valid_until > valid_from",
            name="ck_offers_dates",
        ),
    )

    @property
    def remaining_redemptions(self) -> int | None:
        """Calculate remaining redemptions if maximum is set."""
        if self.max_redemptions is None:
            return None
        return max(0, self.max_redemptions - (self.redemption_count or 0))

    def __repr__(self):
        return f"<Offer(id={self.id}, title='{self.title}', status='{self.status}')>"
