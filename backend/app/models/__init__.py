"""Models Package

Exports all SQLAlchemy models for easy importing.
"""

from app.models.base import BaseModel
from app.models.user import User, UserRole, UserStatus
from app.models.college import College, CollegeStatus
from app.models.campus import Campus
from app.models.student import Student, VerificationStatus
from app.models.category import Category
from app.models.business import (
    Business,
    BusinessStatus,
    BusinessVerificationStatus,
    PriceLevel,
)
from app.models.business_hours import BusinessHours
from app.models.service import Service
from app.models.service_price_history import ServicePriceHistory
from app.models.rating_dimension import RatingDimension
from app.models.review import Review, ReviewStatus, VerificationLevel
from app.models.review_rating import ReviewRating
from app.models.review_photo import ReviewPhoto
from app.models.review_response import ReviewResponse
from app.models.review_report import (
    ReviewReport,
    ReviewReportReason,
    ReviewReportStatus,
)
from app.models.business_photo import (
    BusinessPhoto,
    BusinessPhotoStatus,
    BusinessPhotoUploaderType,
)
from app.models.favorite import Favorite
from app.models.offer import Offer, OfferDiscountType, OfferStatus
from app.models.offer_redemption import OfferRedemption, OfferRedemptionStatus
from app.models.business_report import (
    BusinessReport,
    BusinessReportReason,
    BusinessReportStatus,
)
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.business_interaction import BusinessInteraction, InteractionType

__all__ = [
    # Base
    "BaseModel",
    # User
    "User",
    "UserRole",
    "UserStatus",
    # College
    "College",
    "CollegeStatus",
    # Campus
    "Campus",
    # Student
    "Student",
    "VerificationStatus",
    # Category
    "Category",
    # Business
    "Business",
    "BusinessStatus",
    "BusinessVerificationStatus",
    "PriceLevel",
    "BusinessHours",
    "Service",
    "ServicePriceHistory",
    # Reviews & Ratings
    "RatingDimension",
    "Review",
    "ReviewStatus",
    "VerificationLevel",
    "ReviewRating",
    "ReviewPhoto",
    "ReviewResponse",
    "ReviewReport",
    "ReviewReportReason",
    "ReviewReportStatus",
    # Business Photos & Favorites
    "BusinessPhoto",
    "BusinessPhotoStatus",
    "BusinessPhotoUploaderType",
    "Favorite",
    # Offers & Redemptions
    "Offer",
    "OfferDiscountType",
    "OfferStatus",
    "OfferRedemption",
    "OfferRedemptionStatus",
    # Reports & Moderation
    "BusinessReport",
    "BusinessReportReason",
    "BusinessReportStatus",
    # Audit Logs
    "AuditLog",
    # Notifications
    "Notification",
    # Analytics & Interactions
    "BusinessInteraction",
    "InteractionType",
]
