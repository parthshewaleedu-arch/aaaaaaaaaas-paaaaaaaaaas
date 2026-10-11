"""Business Model

Core business listing model.
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum

from app.models.base import BaseModel


class BusinessStatus(str, enum.Enum):
    """Business status enumeration."""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REJECTED = "REJECTED"
    REMOVED = "REMOVED"


class BusinessVerificationStatus(str, enum.Enum):
    """Business verification status enumeration."""

    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"


class PriceLevel(str, enum.Enum):
    """Price level enumeration."""

    LEVEL_1 = "₹"
    LEVEL_2 = "₹₹"
    LEVEL_3 = "₹₹₹"
    LEVEL_4 = "₹₹₹₹"


# Association table for business categories (many-to-many)
business_categories = Table(
    "business_categories",
    BaseModel.metadata,
    Column(
        "business_id",
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Business(BaseModel):
    """Business listing model.

    Represents businesses registered on the platform.
    Includes geospatial data for location-based discovery.
    """

    __tablename__ = "businesses"

    # Owner relationship
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Campus relationship
    campus_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campuses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Contact information
    phone = Column(String(20), nullable=False)
    whatsapp = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website_url = Column(Text, nullable=True)

    # Location
    address = Column(Text, nullable=False)
    latitude = Column(Numeric(precision=10, scale=8), nullable=False)
    longitude = Column(Numeric(precision=11, scale=8), nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)

    # Status
    status = Column(
        Enum(BusinessStatus, name="business_status", create_type=True),
        nullable=False,
        default=BusinessStatus.PENDING,
        index=True,
    )
    verification_status = Column(
        Enum(
            BusinessVerificationStatus,
            name="business_verification_status",
            create_type=True,
        ),
        nullable=False,
        default=BusinessVerificationStatus.UNVERIFIED,
        index=True,
    )

    # Business attributes
    price_level = Column(
        Enum(PriceLevel, name="price_level", create_type=True),
        nullable=True,
    )
    student_discount = Column(Boolean, nullable=False, default=False)
    student_discount_description = Column(Text, nullable=True)

    # Cached statistics (denormalized for performance)
    average_rating = Column(Numeric(precision=3, scale=2), nullable=True)
    review_count = Column(Integer, nullable=False, default=0)

    # Verification fields
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Soft deletion
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    owner = relationship("User", backref="businesses")
    campus = relationship("Campus", back_populates="businesses")
    categories = relationship(
        "Category", secondary="business_categories", back_populates="businesses"
    )
    hours = relationship(
        "BusinessHours",
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="BusinessHours.day_of_week",
    )
    services = relationship(
        "Service",
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="Service.name",
    )
    reviews = relationship(
        "Review",
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="desc(Review.created_at)",
    )
    photos = relationship(
        "BusinessPhoto",
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="desc(BusinessPhoto.created_at)",
    )
    favorites = relationship(
        "Favorite",
        back_populates="business",
        cascade="all, delete-orphan",
    )
    offers = relationship(
        "Offer",
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="desc(Offer.created_at)",
    )
    reports = relationship(
        "BusinessReport",
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="desc(BusinessReport.created_at)",
    )
    interactions = relationship(
        "BusinessInteraction",
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="desc(BusinessInteraction.created_at)",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="ck_businesses_latitude",
        ),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="ck_businesses_longitude",
        ),
        CheckConstraint(
            "average_rating IS NULL OR (average_rating >= 1 AND average_rating <= 5)",
            name="ck_businesses_rating",
        ),
        CheckConstraint(
            "review_count >= 0",
            name="ck_businesses_review_count",
        ),
    )

    def __repr__(self):
        return f"<Business(id={self.id}, name={self.name})>"
