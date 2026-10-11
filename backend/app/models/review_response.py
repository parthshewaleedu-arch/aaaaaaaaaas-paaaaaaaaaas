"""Review Response Model

Represents a formal response from a business owner to a student review.
"""

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ReviewResponse(BaseModel):
    """Business owner's response to a customer review.

    Constraint: At most one official response per review.
    """

    __tablename__ = "review_responses"

    review_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    response_text = Column(Text, nullable=False)

    # Relationships
    review = relationship("Review", back_populates="response")
    owner = relationship("User")

    def __repr__(self):
        return f"<ReviewResponse(id={self.id}, review_id={self.review_id}, owner_id={self.owner_id})>"
