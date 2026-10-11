"""Service Endpoints

API routes for service item details, updates, deletions, and price transparency logs.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.service import (
    ServicePriceHistoryResponse,
    ServiceResponse,
    ServiceUpdate,
)
from app.services.business_service import BusinessService
from app.services.service_service import ServiceService

router = APIRouter()


@router.get(
    "/{service_id}", response_model=ServiceResponse, summary="Get service by ID"
)
async def get_service(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific service offering.
    Public endpoint.
    """
    service = ServiceService.get_service_by_id(service_id, db)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    service.days_since_update = ServiceService.calculate_days_since_update(
        service.updated_at
    )
    return service


@router.patch(
    "/{service_id}", response_model=ServiceResponse, summary="Update service (owner)"
)
async def update_service(
    service_id: UUID,
    update_data: ServiceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update service details or pricing.
    If the price changes, a price history record is automatically created.
    Requires OWNER role (owner of the business) or ADMIN.
    """
    service = ServiceService.get_service_by_id(service_id, db)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    if current_user.role != UserRole.ADMIN and not BusinessService.check_ownership(
        service.business_id, current_user.id, db
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this service",
        )

    updated = ServiceService.update_service(
        service_id=service_id,
        update_data=update_data,
        db=db,
        changed_by=current_user.id,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    updated.days_since_update = ServiceService.calculate_days_since_update(
        updated.updated_at
    )
    return updated


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete service (owner)",
)
async def delete_service(
    service_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a service offering from a business.
    Requires OWNER role (owner of the business) or ADMIN.
    """
    service = ServiceService.get_service_by_id(service_id, db)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    if current_user.role != UserRole.ADMIN and not BusinessService.check_ownership(
        service.business_id, current_user.id, db
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this service",
        )

    deleted = ServiceService.delete_service(service_id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )
    return None


@router.get(
    "/{service_id}/price-history",
    response_model=list[ServicePriceHistoryResponse],
    summary="Get service price history",
)
async def get_service_price_history(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get full price change audit trail for transparency and trust tracking.
    Public endpoint.
    """
    service = ServiceService.get_service_by_id(service_id, db)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return ServiceService.get_price_history(service_id, db)
