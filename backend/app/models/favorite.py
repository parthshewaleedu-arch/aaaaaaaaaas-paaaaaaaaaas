"""Favorite Model

Represents a saved or bookmarked business for a student or user.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Favorite(Base):
    """Favorite / bookmark junction table."""

    __tablename__ = "favorites"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="favorites")
    business = relationship("Business", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, business_id={self.business_id})>"
