"""Business Photo Model

Represents photos uploaded for a business gallery by owners, students, or admins.
"""

import enum

from sqlalchemy import Boolean, CheckConstraint, Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class BusinessPhotoUploaderType(str, enum.Enum):
    """Type of user that uploaded the business photo."""

    OWNER = "OWNER"
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class BusinessPhotoStatus(str, enum.Enum):
    """Lifecycle and moderation status of business photo."""

    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"
    PENDING_MODERATION = "PENDING_MODERATION"


class BusinessPhoto(BaseModel):
    """Photo uploaded for a business gallery."""

    __tablename__ = "business_photos"

    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url = Column(Text, nullable=False)
    caption = Column(String(255), nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    uploader_type = Column(
        Enum(
            BusinessPhotoUploaderType,
            name="business_photo_uploader_type",
            create_type=True,
        ),
        nullable=False,
        default=BusinessPhotoUploaderType.OWNER,
    )
    status = Column(
        Enum(BusinessPhotoStatus, name="business_photo_status", create_type=True),
        nullable=False,
        default=BusinessPhotoStatus.ACTIVE,
        index=True,
    )

    # Relationships
    business = relationship("Business", back_populates="photos")
    uploader = relationship("User", back_populates="photos")

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'REMOVED', 'PENDING_MODERATION')",
            name="ck_business_photos_status",
        ),
        CheckConstraint(
            "uploader_type IN ('OWNER', 'STUDENT', 'ADMIN')",
            name="ck_business_photos_uploader",
        ),
    )

    def __repr__(self):
        return f"<BusinessPhoto(id={self.id}, business_id={self.business_id}, is_primary={self.is_primary})>"
