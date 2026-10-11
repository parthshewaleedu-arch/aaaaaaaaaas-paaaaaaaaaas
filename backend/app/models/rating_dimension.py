"""Rating Dimension Model

Defines category-specific evaluation aspects (e.g., Food quality, Hygiene, Equipment).
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class RatingDimension(BaseModel):
    """Rating dimension model for category-specific multi-dimensional reviews.

    Enables tailored reviews (e.g. Mess: Food Quality, Hygiene, Quantity; Gym: Equipment, Cleanliness).
    """

    __tablename__ = "rating_dimensions"

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)

    # Relationships
    category = relationship("Category", back_populates="rating_dimensions")
    review_ratings = relationship(
        "ReviewRating", back_populates="dimension", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("category_id", "slug", name="uq_rating_dimensions"),
    )

    def __repr__(self):
        return f"<RatingDimension(id={self.id}, name={self.name}, slug={self.slug})>"
