"""Review Endpoints

API routes for review management, updates, deletions, helpful voting,
business owner responses, and moderation reports.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.models.user import User, UserRole
from app.schemas.review import (
    ReviewDetailResponse,
    ReviewOwnerResponseCreate,
    ReviewReportCreate,
    ReviewReportResponse,
    ReviewResponseItem,
    ReviewUpdate,
)
from app.services.review_service import ReviewService

router = APIRouter()


@router.get(
    "/{review_id}", response_model=ReviewDetailResponse, summary="Get review by ID"
)
async def get_review(
    review_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific review.
    Public endpoint.
    """
    review = ReviewService.get_review_by_id(review_id, db)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return ReviewService.serialize_review_detail(review, db)


@router.patch(
    "/{review_id}",
    response_model=ReviewDetailResponse,
    summary="Update review (student)",
)
async def update_review(
    review_id: UUID,
    update_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update student's own review.
    Requires STUDENT role.
    """
    try:
        updated = ReviewService.update_review(
            review_id=review_id,
            user_id=current_user.id,
            update_data=update_data,
            db=db,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return ReviewService.serialize_review_detail(updated, db)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete review (student / admin)",
)
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete own review (student) or remove violating review (admin).
    """
    try:
        is_admin = current_user.role == UserRole.ADMIN
        success = ReviewService.delete_review(
            review_id=review_id,
            user_id=current_user.id,
            db=db,
            is_admin=is_admin,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return None


@router.post(
    "/{review_id}/response",
    response_model=ReviewResponseItem,
    status_code=status.HTTP_201_CREATED,
    summary="Respond to review (owner)",
    dependencies=[
        Depends(rate_limit(limit=20, window_seconds=60, key_prefix="resp_rev"))
    ],
)
async def respond_to_review(
    review_id: UUID,
    response_data: ReviewOwnerResponseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Business owner replies to a customer review.
    Requires OWNER role (owner of the reviewed business) or ADMIN.
    """
    try:
        resp = ReviewService.respond_to_review(
            review_id=review_id,
            owner_id=current_user.id,
            response_text=response_data.response_text,
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

    return ReviewResponseItem(
        id=resp.id,
        response_text=resp.response_text,
        created_at=resp.created_at,
        updated_at=resp.updated_at,
    )


@router.post(
    "/{review_id}/report",
    response_model=ReviewReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report review",
    dependencies=[
        Depends(rate_limit(limit=10, window_seconds=60, key_prefix="report_rev"))
    ],
)
async def report_review(
    review_id: UUID,
    report_data: ReviewReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Report a problematic or policy-violating review.
    Requires authentication.
    """
    try:
        report = ReviewService.report_review(
            review_id=review_id,
            reported_by=current_user.id,
            reason=report_data.reason,
            description=report_data.description,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return ReviewReportResponse(
        id=report.id,
        review_id=report.review_id,
        reported_by=report.reported_by,
        reason=str(
            report.reason.value if hasattr(report.reason, "value") else report.reason
        ),
        description=report.description,
        status=str(
            report.status.value if hasattr(report.status, "value") else report.status
        ),
        created_at=report.created_at,
    )


@router.post(
    "/{review_id}/helpful",
    response_model=ReviewDetailResponse,
    summary="Vote review as helpful",
    dependencies=[
        Depends(rate_limit(limit=30, window_seconds=60, key_prefix="vote_helpful"))
    ],
)
async def vote_helpful(
    review_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Mark a review as helpful.
    Requires authentication.
    """
    review = ReviewService.vote_helpful(review_id, db)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return ReviewService.serialize_review_detail(review, db)
