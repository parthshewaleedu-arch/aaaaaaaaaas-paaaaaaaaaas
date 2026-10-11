"""Service Model

Offerings and services provided by businesses.
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Service(BaseModel):
    """Service model for business offerings.

    Tracks price, currency, units (e.g. per plate, per month, per page),
    and links to price history.
    """

    __tablename__ = "services"

    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    unit = Column(String(50), nullable=True)  # e.g., 'plate', 'month', 'page', 'hour'
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Relationships
    business = relationship("Business", back_populates="services")
    price_history = relationship(
        "ServicePriceHistory",
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="desc(ServicePriceHistory.effective_from)",
    )

    __table_args__ = (CheckConstraint("price >= 0", name="ck_services_price"),)

    def __repr__(self):
        return f"<Service(id={self.id}, name={self.name}, price={self.price} {self.currency})>"
