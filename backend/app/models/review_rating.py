"""Review Rating Model

Stores dimensional rating scores (e.g., Food quality: 5, Hygiene: 4) for a review.
"""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ReviewRating(BaseModel):
    """Dimensional score breakdown for a specific review and rating dimension."""

    __tablename__ = "review_ratings"

    review_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dimension_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rating_dimensions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating = Column(Integer, nullable=False)

    # Relationships
    review = relationship("Review", back_populates="ratings")
    dimension = relationship("RatingDimension", back_populates="review_ratings")

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_review_ratings_rating",
        ),
        UniqueConstraint("review_id", "dimension_id", name="uq_review_ratings"),
    )

    def __repr__(self):
        return f"<ReviewRating(review_id={self.review_id}, dimension_id={self.dimension_id}, rating={self.rating})>"
