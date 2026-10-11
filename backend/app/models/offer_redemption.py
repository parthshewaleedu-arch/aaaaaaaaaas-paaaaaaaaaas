"""Offer Redemption Model.

Tracks student redemptions of promotional offers, verification codes, and merchant validations.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class OfferRedemptionStatus(str, PyEnum):
    """Lifecycle status of an offer redemption."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class OfferRedemption(Base):
    """OfferRedemption model recording each redemption event."""

    __tablename__ = "offer_redemptions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    offer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("offers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    redeemed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    status = Column(
        Enum(
            OfferRedemptionStatus,
            name="offer_redemption_status",
            create_type=True,
        ),
        nullable=False,
        default=OfferRedemptionStatus.PENDING,
    )
    verification_code = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    offer = relationship("Offer", back_populates="redemptions")
    user = relationship("User", back_populates="offer_redemptions")

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'COMPLETED', 'CANCELLED', 'EXPIRED')",
            name="ck_offer_redemptions_status",
        ),
    )

    def __repr__(self):
        return f"<OfferRedemption(id={self.id}, code='{self.verification_code}', status='{self.status}')>"
