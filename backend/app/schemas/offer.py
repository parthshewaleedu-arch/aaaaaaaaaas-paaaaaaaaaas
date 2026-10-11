"""Offer Schemas.

Pydantic validation schemas for business offers, discounts, and redemptions.
"""

from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.offer import OfferDiscountType, OfferStatus
from app.models.offer_redemption import OfferRedemptionStatus


class OfferBusinessInfo(BaseModel):
    """Minimal business info for offer response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    address: Optional[str] = None
    campus_id: Optional[UUID] = None
    average_rating: Optional[float] = None


class OfferBase(BaseModel):
    """Base schema for business offers."""

    title: str = Field(
        ..., min_length=1, max_length=255, description="Offer headline/title"
    )
    description: str = Field(..., min_length=1, description="Details of the offer")
    discount_type: OfferDiscountType = Field(
        ..., description="PERCENTAGE, FIXED_AMOUNT, or SERVICE_DISCOUNT"
    )
    discount_value: float = Field(
        ..., gt=0, description="Numerical discount amount or percent"
    )
    terms_conditions: Optional[str] = Field(
        None, description="Terms, restrictions, and conditions"
    )
    valid_from: datetime = Field(..., description="Start date/time in UTC")
    valid_until: datetime = Field(..., description="Expiration date/time in UTC")
    max_redemptions: Optional[int] = Field(
        None, gt=0, description="Cap on total redemptions, or null for unlimited"
    )


class OfferCreate(OfferBase):
    """Schema for creating a new business offer."""

    status: Optional[OfferStatus] = Field(
        OfferStatus.ACTIVE, description="Initial status (ACTIVE or DRAFT)"
    )

    @model_validator(mode="after")
    def validate_offer_rules(self):
        """Validate logical business rules on create."""
        if self.valid_until <= self.valid_from:
            raise ValueError("valid_until must be strictly after valid_from")
        if (
            self.discount_type == OfferDiscountType.PERCENTAGE
            and self.discount_value > 100
        ):
            raise ValueError("Percentage discount cannot exceed 100%")
        return self


class OfferUpdate(BaseModel):
    """Schema for updating an existing offer."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    discount_type: Optional[OfferDiscountType] = None
    discount_value: Optional[float] = Field(None, gt=0)
    terms_conditions: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_redemptions: Optional[int] = Field(None, gt=0)
    status: Optional[OfferStatus] = None

    @model_validator(mode="after")
    def validate_update_rules(self):
        """Validate dates and percentages if updated."""
        if self.valid_from and self.valid_until and self.valid_until <= self.valid_from:
            raise ValueError("valid_until must be strictly after valid_from")
        if (
            self.discount_type == OfferDiscountType.PERCENTAGE
            and self.discount_value is not None
            and self.discount_value > 100
        ):
            raise ValueError("Percentage discount cannot exceed 100%")
        return self


class OfferResponse(BaseModel):
    """Schema for serialized offer response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    business: Optional[OfferBusinessInfo] = None
    title: str
    description: str
    discount_type: OfferDiscountType
    discount_value: float
    terms_conditions: Optional[str] = None
    valid_from: datetime
    valid_until: datetime
    max_redemptions: Optional[int] = None
    redemption_count: int = 0
    remaining_redemptions: Optional[int] = None
    status: OfferStatus
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None


class OfferListResponse(BaseModel):
    """Paginated list of offers."""

    items: List[OfferResponse]
    total: int
    page: int = 1
    limit: int = 20


class OfferRedeemResponse(BaseModel):
    """Response returned upon student redeeming an offer."""

    success: bool = True
    redemption_id: UUID
    offer_id: UUID
    verification_code: str
    expires_at: Optional[datetime] = None
    status: OfferRedemptionStatus
    message: str = "Offer redeemed. Show verification code to merchant."


class OfferRedemptionResponse(BaseModel):
    """Serialized representation of a student redemption."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    offer_id: UUID
    user_id: UUID
    redeemed_at: datetime
    status: OfferRedemptionStatus
    verification_code: str
    expires_at: Optional[datetime] = None
    offer: Optional[OfferResponse] = None


class OfferRedemptionListResponse(BaseModel):
    """List of redemptions for student or business owner."""

    items: List[OfferRedemptionResponse]
    total: int


class OfferRedemptionValidateRequest(BaseModel):
    """Request by merchant to validate and complete a redemption."""

    verification_code: str = Field(
        ...,
        min_length=4,
        max_length=50,
        description="Verification code shown by student",
    )


class OfferRedemptionValidateResponse(BaseModel):
    """Confirmation response upon merchant validating a student code."""

    success: bool = True
    message: str = "Redemption successfully validated and completed."
    redemption_id: UUID
    offer_id: UUID
    offer_title: str
    discount_type: OfferDiscountType
    discount_value: float
    student_id: UUID
    student_display_name: str
    status: OfferRedemptionStatus = OfferRedemptionStatus.COMPLETED
