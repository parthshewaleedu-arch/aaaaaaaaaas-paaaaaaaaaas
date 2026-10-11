"""Service Schemas

Pydantic schemas for business services and price history tracking.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):
    """Base schema for a business service."""

    name: str = Field(..., min_length=1, max_length=255, description="Service name")
    description: Optional[str] = Field(None, description="Detailed description")
    price: float = Field(..., ge=0, description="Price in currency unit")
    currency: str = Field("INR", max_length=3, description="Currency code (e.g. INR)")
    unit: Optional[str] = Field(
        None, max_length=50, description="Pricing unit, e.g. plate, month, page"
    )
    is_active: bool = Field(True, description="Whether the service is actively offered")


class ServiceCreate(BaseModel):
    """Schema for adding a service to a business."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    currency: str = Field("INR", max_length=3)
    unit: Optional[str] = None


class ServiceUpdate(BaseModel):
    """Schema for updating an existing service."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class ServicePriceHistoryResponse(BaseModel):
    """Schema for price history audit log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_id: UUID
    price: float
    currency: str
    effective_from: datetime
    effective_to: Optional[datetime] = None
    changed_by: Optional[UUID] = None


class ServiceResponse(BaseModel):
    """Schema for service details response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    name: str
    description: Optional[str] = None
    price: float
    currency: str
    unit: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    days_since_update: Optional[int] = None
    price_history: list[ServicePriceHistoryResponse] = []


class ServiceListResponse(BaseModel):
    """Schema for list of services."""

    items: list[ServiceResponse]
    total: int
