"""Service Price History Model

Tracks price changes over time for transparency and trust metrics.
"""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ServicePriceHistory(BaseModel):
    """Historical record of service price changes.

    Enables 'Price updated X days ago' trust indicators.
    """

    __tablename__ = "service_price_history"

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    effective_from = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    effective_to = Column(DateTime(timezone=True), nullable=True)
    changed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    service = relationship("Service", back_populates="price_history")
    user = relationship("User")

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_service_price_history_price"),
    )

    def __repr__(self):
        return (
            f"<ServicePriceHistory(service_id={self.service_id}, price={self.price}, "
            f"effective_from={self.effective_from})>"
        )
