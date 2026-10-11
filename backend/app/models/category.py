"""Category Model

Hierarchical category system for businesses.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Category(BaseModel):
    """Category model for business classification.

    Supports hierarchical categories (parent-child relationships).
    """

    __tablename__ = "categories"

    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    display_order = Column(Integer, nullable=False, default=0)

    # Relationships
    parent = relationship("Category", remote_side="Category.id", backref="children")
    businesses = relationship(
        "Business", secondary="business_categories", back_populates="categories"
    )
    rating_dimensions = relationship(
        "RatingDimension",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="RatingDimension.display_order",
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"
