"""User Model

Core user account model supporting all roles (STUDENT, OWNER, ADMIN, COLLEGE_ADMIN).
"""

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration."""

    STUDENT = "STUDENT"
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    COLLEGE_ADMIN = "COLLEGE_ADMIN"


class UserStatus(str, enum.Enum):
    """User status enumeration."""

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"
    PENDING = "PENDING"


class User(BaseModel):
    """User account model.

    Represents core user accounts for all roles in the system.
    Password is stored as a hash (Argon2/bcrypt), never plaintext.
    """

    __tablename__ = "users"

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)

    # Role and Status
    role = Column(
        Enum(UserRole, name="user_role", create_type=True),
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(UserStatus, name="user_status", create_type=True),
        nullable=False,
        default=UserStatus.ACTIVE,
        index=True,
    )

    # Verification
    is_email_verified = Column(Boolean, nullable=False, default=False)
    is_phone_verified = Column(Boolean, nullable=False, default=False)

    # Activity tracking
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Soft deletion
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    reviews = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )
    photos = relationship(
        "BusinessPhoto", back_populates="uploader", cascade="all, delete-orphan"
    )
    favorites = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )
    offer_redemptions = relationship(
        "OfferRedemption",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(OfferRedemption.redeemed_at)",
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(Notification.created_at)",
    )

    @property
    def is_active(self) -> bool:
        """Return True if user status is ACTIVE."""
        return self.status == UserStatus.ACTIVE

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
