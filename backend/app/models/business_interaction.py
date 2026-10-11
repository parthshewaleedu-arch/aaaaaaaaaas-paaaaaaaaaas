"""Business Interaction Model.

Tracks student/user engagement actions on business profiles for owner KPI analytics
(profile views, direction clicks, call clicks, offer views, search appearances).
"""

from sqlalchemy import Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class InteractionType(str, enum.Enum):
    """Interaction event types."""

    PROFILE_VIEW = "PROFILE_VIEW"
    DIRECTION_CLICK = "DIRECTION_CLICK"
    CALL_CLICK = "CALL_CLICK"
    OFFER_VIEW = "OFFER_VIEW"
    SEARCH_APPEARANCE = "SEARCH_APPEARANCE"


class BusinessInteraction(BaseModel):
    """Business engagement interaction record."""

    __tablename__ = "business_interactions"

    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    interaction_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    # Relationships
    business = relationship("Business", back_populates="interactions")
    user = relationship("User")

    __table_args__ = (
        Index(
            "ix_business_interactions_business_type",
            "business_id",
            "interaction_type",
        ),
        Index("ix_business_interactions_created_at", "business_id", "created_at"),
    )

    def __repr__(self):
        return (
            f"<BusinessInteraction(id={self.id}, business_id={self.business_id}, "
            f"type={self.interaction_type})>"
        )
