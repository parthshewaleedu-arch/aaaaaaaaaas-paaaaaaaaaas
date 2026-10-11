"""Business endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.auth.dependencies import (
    get_current_active_user,
    get_optional_current_user,
)
from app.models.user import User, UserRole
from app.models.business import BusinessStatus, BusinessVerificationStatus
from app.services.business_service import BusinessService
from app.schemas.business import (
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessDetailResponse,
    BusinessListResponse,
    BusinessVerificationRequest,
    BusinessStatusUpdate,
    BusinessVerificationUpdate,
    BusinessHoursBatchUpdate,
    BusinessHoursScheduleResponse,
)
from app.schemas.business_photo import BusinessPhotoCreate, BusinessPhotoResponse
from app.schemas.favorite import FavoriteActionResponse, FavoriteStatusResponse
from app.schemas.map import DirectionsResponse
from app.schemas.offer import (
    OfferCreate,
    OfferListResponse,
    OfferRedemptionValidateRequest,
    OfferRedemptionValidateResponse,
    OfferResponse,
)
from app.schemas.rating_dimension import RatingDimensionResponse
from app.schemas.report import BusinessReportCreate, BusinessReportResponse
from app.schemas.review import (
    ReviewCreate,
    ReviewDetailResponse,
    ReviewListResponse,
)
from app.schemas.owner_analytics import (
    BusinessAnalyticsResponse,
    BusinessInteractionCreate,
    BusinessInteractionResponse,
)
from app.schemas.service import ServiceCreate, ServiceResponse
from app.services.business_photo_service import BusinessPhotoService
from app.services.favorite_service import FavoriteService
from app.services.map_service import MapService
from app.services.offer_service import OfferService
from app.services.owner_analytics_service import OwnerAnalyticsService
from app.services.report_service import ReportService
from app.services.review_service import ReviewService
from app.services.service_service import ServiceService

router = APIRouter()


# Owner endpoints


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create business",
)
async def create_business(
    business_data: BusinessCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new business.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business owners can create businesses",
        )

    # Check if owner already has a business
    existing = BusinessService.get_business_by_owner(current_user.id, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner already has a business",
        )

    try:
        business = BusinessService.create_business(business_data, current_user.id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return business


@router.get(
    "/my-business", response_model=BusinessDetailResponse, summary="Get my business"
)
async def get_my_business(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get the current authenticated owner's business with full details.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business owners can access this endpoint",
        )

    business = BusinessService.get_business_by_owner(current_user.id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business


@router.patch(
    "/my-business", response_model=BusinessResponse, summary="Update my business"
)
async def update_my_business(
    business_data: BusinessUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update the current authenticated owner's business.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business owners can access this endpoint",
        )

    business = BusinessService.get_business_by_owner(current_user.id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    try:
        updated = BusinessService.update_business(business.id, business_data, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return updated


@router.post(
    "/my-business/submit-verification",
    response_model=BusinessResponse,
    summary="Submit business for verification",
)
async def submit_my_business_verification(
    verification_request: Optional[BusinessVerificationRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Submit the current owner's business for verification.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business owners can access this endpoint",
        )

    business = BusinessService.get_business_by_owner(current_user.id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    try:
        notes = verification_request.notes if verification_request else None
        documents = verification_request.documents if verification_request else None
        updated = BusinessService.submit_for_verification(
            business.id, current_user.id, db, notes=notes, documents=documents
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return updated


# Admin pending verification endpoint (must be defined before /{business_id} to avoid collision)


@router.get(
    "/admin/pending-verification",
    response_model=BusinessListResponse,
    summary="List pending verifications (admin)",
)
async def list_pending_verifications(
    campus_id: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all businesses awaiting verification review.
    Requires ADMIN role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    skip = (page - 1) * page_size
    businesses = BusinessService.list_businesses(
        db=db,
        campus_id=campus_id,
        verification_status=BusinessVerificationStatus.PENDING,
        sort="newest",
        skip=skip,
        limit=page_size,
    )
    total = BusinessService.count_businesses(
        db=db,
        campus_id=campus_id,
        verification_status=BusinessVerificationStatus.PENDING,
    )

    return BusinessListResponse(
        items=businesses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )


# Public endpoints


@router.get(
    "", response_model=BusinessListResponse, summary="List and search businesses"
)
async def list_businesses(
    search: Optional[str] = Query(
        None, description="Search query for business name or description"
    ),
    campus_id: Optional[UUID] = None,
    status: Optional[BusinessStatus] = None,
    verification_status: Optional[BusinessVerificationStatus] = Query(
        None, alias="verification_status"
    ),
    verified_only: Optional[bool] = Query(
        False, description="Filter only verified businesses"
    ),
    category_id: Optional[UUID] = None,
    min_rating: Optional[float] = Query(
        None, ge=1.0, le=5.0, description="Minimum average rating (1-5)"
    ),
    price_level: Optional[str] = Query(
        None, pattern=r"^₹{1,4}$", description="Price level filter (₹ to ₹₹₹₹)"
    ),
    student_discount: Optional[bool] = Query(
        None, description="Filter for student discounts"
    ),
    open_now: Optional[bool] = Query(
        None, description="Filter for currently open businesses"
    ),
    latitude: Optional[float] = Query(
        None, ge=-90, le=90, description="Latitude for proximity search"
    ),
    longitude: Optional[float] = Query(
        None, ge=-180, le=180, description="Longitude for proximity search"
    ),
    radius_meters: Optional[int] = Query(
        None, gt=0, le=50000, description="Maximum distance in meters"
    ),
    sort: Optional[str] = Query(
        "newest", pattern=r"^(relevance|rating|distance|newest|name)$"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search and filter businesses with pagination.
    Supports text search, category hierarchy, ratings, discounts, and geospatial proximity.
    Public endpoint.
    """
    skip = (page - 1) * page_size

    businesses = BusinessService.list_businesses(
        db=db,
        campus_id=campus_id,
        status=status,
        verification_status=verification_status,
        verified_only=verified_only,
        category_id=category_id,
        search=search,
        min_rating=min_rating,
        price_level=price_level,
        student_discount=student_discount,
        open_now=open_now,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
        sort=sort,
        skip=skip,
        limit=page_size,
    )

    total = BusinessService.count_businesses(
        db=db,
        campus_id=campus_id,
        status=status,
        verification_status=verification_status,
        verified_only=verified_only,
        category_id=category_id,
        search=search,
        min_rating=min_rating,
        price_level=price_level,
        student_discount=student_discount,
        open_now=open_now,
    )

    return BusinessListResponse(
        items=businesses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )


@router.get(
    "/{business_id}",
    response_model=BusinessDetailResponse,
    summary="Get business by ID",
)
async def get_business(
    business_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a business by ID with full details.
    """
    business = BusinessService.get_business_by_id(business_id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business


@router.get(
    "/{business_id}/directions",
    response_model=DirectionsResponse,
    summary="Get walking directions and navigation metrics to business",
)
async def get_business_directions(
    business_id: UUID,
    user_lat: float = Query(..., ge=-90, le=90, description="Current user latitude"),
    user_lng: float = Query(..., ge=-180, le=180, description="Current user longitude"),
    db: Session = Depends(get_db),
):
    """Calculate distance, walking duration, compass bearing, and Google Maps walking route link.

    Public endpoint.
    """
    return MapService.get_directions(
        business_id=business_id,
        user_lat=user_lat,
        user_lng=user_lng,
        db=db,
    )


@router.get(
    "/{business_id}/hours",
    response_model=BusinessHoursScheduleResponse,
    summary="Get business hours",
)
async def get_business_hours(
    business_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get operating hours schedule for a business.
    Public endpoint.
    """
    business = BusinessService.get_business_by_id(business_id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    hours = BusinessService.get_business_hours(business_id, db)
    is_open, current_status = BusinessService.calculate_open_status(hours)

    return BusinessHoursScheduleResponse(
        is_open_now=is_open,
        current_status=current_status,
        hours=hours,
    )


@router.put(
    "/{business_id}/hours",
    response_model=BusinessHoursScheduleResponse,
    summary="Set business hours (owner)",
)
async def update_business_hours(
    business_id: UUID,
    hours_update: BusinessHoursBatchUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Set or update weekly operating hours for a business.
    Requires OWNER role (owner of this business) or ADMIN.
    """
    if current_user.role != UserRole.ADMIN and not BusinessService.check_ownership(
        business_id, current_user.id, db
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage hours for this business",
        )

    try:
        updated_hours = BusinessService.set_business_hours(
            business_id=business_id,
            hours_data=hours_update.hours,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    is_open, current_status = BusinessService.calculate_open_status(updated_hours)
    return BusinessHoursScheduleResponse(
        is_open_now=is_open,
        current_status=current_status,
        hours=updated_hours,
    )


@router.get(
    "/{business_id}/services",
    response_model=list[ServiceResponse],
    summary="Get business services",
)
async def get_business_services(
    business_id: UUID,
    active_only: bool = Query(True, description="Filter only active offerings"),
    db: Session = Depends(get_db),
):
    """
    Get services offered by a business with freshness and price history indicators.
    Public endpoint.
    """
    business = BusinessService.get_business_by_id(business_id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    services = ServiceService.list_services(business_id, db, active_only=active_only)
    for s in services:
        s.days_since_update = ServiceService.calculate_days_since_update(s.updated_at)
    return services


@router.post(
    "/{business_id}/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add service (owner)",
)
async def create_business_service(
    business_id: UUID,
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Add a new service offering to a business.
    Requires OWNER role (owner of this business) or ADMIN.
    """
    if current_user.role != UserRole.ADMIN and not BusinessService.check_ownership(
        business_id, current_user.id, db
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add services to this business",
        )

    try:
        service = ServiceService.create_service(
            business_id=business_id,
            service_data=service_data,
            db=db,
            changed_by=current_user.id,
        )
        service.days_since_update = ServiceService.calculate_days_since_update(
            service.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return service


@router.get(
    "/{business_id}/reviews",
    response_model=ReviewListResponse,
    summary="Get business reviews",
)
async def get_business_reviews(
    business_id: UUID,
    min_rating: Optional[int] = Query(
        None, ge=1, le=5, description="Minimum rating filter"
    ),
    verification_level: Optional[str] = Query(
        None, description="Filter by verification level"
    ),
    sort: Optional[str] = Query(
        "newest", pattern=r"^(newest|highest_rated|lowest_rated|most_helpful)$"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get reviews for a business with sorting, filtering, and dimensional rating breakdown.
    Public endpoint.
    """
    business = BusinessService.get_business_by_id(business_id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    reviews, total, breakdown = ReviewService.list_reviews(
        business_id=business_id,
        db=db,
        min_rating=min_rating,
        verification_level=verification_level,
        sort=sort,
        page=page,
        page_size=page_size,
    )

    serialized = [ReviewService.serialize_review_detail(r, db) for r in reviews]

    return ReviewListResponse(
        items=serialized,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
        rating_breakdown=breakdown,
    )


@router.post(
    "/{business_id}/reviews",
    response_model=ReviewDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create review (student)",
    dependencies=[
        Depends(rate_limit(limit=15, window_seconds=60, key_prefix="create_rev"))
    ],
)
async def create_business_review(
    business_id: UUID,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Submit a review for a business with overall rating and dimensional evaluation.
    Requires STUDENT role.
    """
    try:
        review = ReviewService.create_review(
            business_id=business_id,
            user_id=current_user.id,
            review_data=review_data,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return ReviewService.serialize_review_detail(review, db)


@router.get(
    "/{business_id}/review-dimensions",
    response_model=list[RatingDimensionResponse],
    summary="Get rating dimensions for business",
)
async def get_business_review_dimensions(
    business_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get category-specific rating dimensions available for evaluating this business.
    Public endpoint.
    """
    business = BusinessService.get_business_by_id(business_id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    dimensions = ReviewService.get_dimensions_for_business(business_id, db)
    return dimensions


# Business Gallery Photos Endpoints


@router.get(
    "/{business_id}/photos",
    response_model=list[BusinessPhotoResponse],
    summary="Get business photos",
)
async def get_business_photos(
    business_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get active gallery photos for a business.
    Public endpoint.
    """
    business = BusinessService.get_business_by_id(business_id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    photos, _ = BusinessPhotoService.list_photos(business_id, db)
    return photos


@router.post(
    "/{business_id}/photos",
    response_model=BusinessPhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload business photo",
)
async def upload_business_photo(
    business_id: UUID,
    photo_data: BusinessPhotoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload a photo to a business gallery.
    Requires authentication (Owner, Student, or Admin).
    """
    try:
        photo = BusinessPhotoService.upload_photo(
            business_id=business_id,
            user=current_user,
            photo_data=photo_data,
            db=db,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return photo


@router.patch(
    "/{business_id}/photos/{photo_id}/primary",
    response_model=BusinessPhotoResponse,
    summary="Set primary cover photo (owner)",
)
async def set_primary_business_photo(
    business_id: UUID,
    photo_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Designate photo as primary cover photo for business.
    Requires OWNER (of this business) or ADMIN.
    """
    try:
        photo = BusinessPhotoService.set_primary_photo(
            business_id=business_id,
            photo_id=photo_id,
            user=current_user,
            db=db,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return photo


@router.delete(
    "/{business_id}/photos/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete business photo",
)
async def delete_business_photo(
    business_id: UUID,
    photo_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a photo from business gallery.
    Allowed for photo uploader, business owner, or platform admin.
    """
    try:
        success = BusinessPhotoService.delete_photo(
            business_id=business_id,
            photo_id=photo_id,
            user=current_user,
            db=db,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    return None


# Business Favorite Status Endpoints


@router.get(
    "/{business_id}/is-favorite",
    response_model=FavoriteStatusResponse,
    summary="Check if business is favorited",
)
async def check_business_is_favorite(
    business_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Check if current user has saved this business to favorites.
    Requires authentication.
    """
    is_fav = FavoriteService.is_favorite(
        user_id=current_user.id,
        business_id=business_id,
        db=db,
    )
    return FavoriteStatusResponse(
        business_id=business_id,
        is_favorite=is_fav,
    )


@router.post(
    "/{business_id}/favorite",
    response_model=FavoriteActionResponse,
    summary="Toggle favorite business",
)
async def toggle_business_favorite(
    business_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Toggle saving/unsaving this business to favorites.
    Requires authentication.
    """
    try:
        is_fav, msg = FavoriteService.toggle_favorite(
            user_id=current_user.id,
            business_id=business_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return FavoriteActionResponse(
        success=True,
        message=msg,
        is_favorite=is_fav,
    )


# Business Offers Endpoints


@router.post(
    "/{business_id}/offers",
    response_model=OfferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create offer for business",
)
async def create_business_offer(
    business_id: UUID,
    offer_in: OfferCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a promotional discount offer for this business.

    Requires business owner or platform admin privileges.
    """
    return OfferService.create_offer(
        business_id=business_id,
        offer_in=offer_in,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/{business_id}/offers",
    response_model=OfferListResponse,
    summary="List business offers",
)
async def list_business_offers(
    business_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """List promotional offers created by this business.

    Public endpoint.
    """
    skip = (page - 1) * limit
    offers, total = OfferService.list_business_offers(
        business_id=business_id,
        db=db,
        skip=skip,
        limit=limit,
    )
    return OfferListResponse(
        items=offers,
        total=total,
        page=page,
        limit=limit,
    )


@router.post(
    "/{business_id}/offers/validate",
    response_model=OfferRedemptionValidateResponse,
    summary="Validate and complete student offer redemption",
)
async def validate_offer_redemption(
    business_id: UUID,
    validation_req: OfferRedemptionValidateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Merchant validates a student's presented verification code and marks it completed.

    Requires business owner or platform admin privileges.
    """
    return OfferService.validate_redemption(
        business_id=business_id,
        verification_code=validation_req.verification_code,
        current_user=current_user,
        db=db,
    )


# Admin endpoints


@router.patch(
    "/{business_id}/status",
    response_model=BusinessResponse,
    summary="Update business status (admin)",
)
async def update_business_status(
    business_id: UUID,
    status_update: BusinessStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update business status.
    Requires ADMIN role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    business = BusinessService.get_business_by_id(business_id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    try:
        business.status = BusinessStatus(status_update.status)
        if status_update.reason:
            business.rejection_reason = status_update.reason
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status",
        )

    db.commit()
    db.refresh(business)
    return business


@router.patch(
    "/{business_id}/verify",
    response_model=BusinessResponse,
    summary="Update business verification (admin)",
)
async def update_business_verification(
    business_id: UUID,
    verification_update: BusinessVerificationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Approve or reject business verification.
    Requires ADMIN role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    business = BusinessService.get_business_by_id(business_id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    if (
        verification_update.action == "APPROVE"
        or verification_update.verification_status == "VERIFIED"
    ):
        updated = BusinessService.approve_business(
            business_id,
            db,
            reviewer_id=current_user.id,
            reason=verification_update.reason,
        )
    elif (
        verification_update.action == "REJECT"
        or verification_update.verification_status in ("UNVERIFIED", "REJECTED")
    ):
        updated = BusinessService.reject_business(
            business_id,
            db,
            reviewer_id=current_user.id,
            reason=verification_update.reason,
        )
    elif verification_update.verification_status:
        try:
            business.verification_status = BusinessVerificationStatus(
                verification_update.verification_status
            )
            db.commit()
            db.refresh(business)
            updated = business
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification status",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify action (APPROVE/REJECT) or verification_status",
        )

    return updated


@router.post(
    "/{id}/report",
    response_model=BusinessReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report a business listing",
    dependencies=[
        Depends(rate_limit(limit=10, window_seconds=60, key_prefix="report_biz"))
    ],
)
def report_business(
    id: UUID,
    report_data: BusinessReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """File a moderation report against a business listing."""
    return ReportService.create_business_report(
        business_id=id,
        reported_by=current_user.id,
        data=report_data,
        db=db,
    )


@router.post(
    "/{id}/interactions",
    response_model=BusinessInteractionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record customer interaction event",
)
def record_business_interaction(
    id: UUID,
    interaction_data: BusinessInteractionCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Log user engagement signals (PROFILE_VIEW, DIRECTION_CLICK, CALL_CLICK, OFFER_VIEW).
    Supports both anonymous visitors and authenticated users.
    """
    return OwnerAnalyticsService.record_interaction(
        db=db,
        business_id=id,
        interaction_type=interaction_data.interaction_type.value,
        user_id=current_user.id if current_user else None,
    )


@router.get(
    "/{id}/analytics",
    response_model=BusinessAnalyticsResponse,
    summary="Get business analytics",
)
def get_business_analytics(
    id: UUID,
    days: int = Query(30, ge=1, le=365, description="Period in days"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed performance metrics for a business listing.
    Only the business owner or platform administrator can view analytics.
    """
    business = BusinessService.get_business_by_id(id, db)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    if business.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access analytics for this business",
        )

    return OwnerAnalyticsService.get_business_analytics(
        db=db,
        business_id=id,
        days=days,
    )
