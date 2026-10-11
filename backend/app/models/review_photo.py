"""Review Photo Model

Stores photos uploaded alongside a student review.
"""

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ReviewPhoto(BaseModel):
    """Photo attached to a student review."""

    __tablename__ = "review_photos"

    review_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url = Column(Text, nullable=False)

    # Relationships
    review = relationship("Review", back_populates="photos")

    def __repr__(self):
        return f"<ReviewPhoto(id={self.id}, review_id={self.review_id})>"
