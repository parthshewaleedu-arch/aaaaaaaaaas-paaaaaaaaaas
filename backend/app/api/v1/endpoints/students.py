from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.student import VerificationStatus
from app.models.user import User, UserRole
from app.schemas.favorite import FavoriteActionResponse, FavoriteListResponse
from app.schemas.student import (
    StudentProfileResponse,
    StudentResponse,
    StudentUpdate,
    StudentVerificationResponse,
)
from app.services.college_verification_service import CollegeVerificationService
from app.services.favorite_service import FavoriteService
from app.services.student_service import StudentService

router = APIRouter()


@router.post("/verify-college-email", summary="Request college email verification")
async def request_college_email_verification(
    student_id: str,
    db: Session = Depends(get_db),
):
    """
    Request college email verification.
    Sends a verification email to the student's college email.
    """
    success = CollegeVerificationService.request_verification(student_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return {
        "success": True,
        "message": "Verification email sent. Please check your college email.",
    }


@router.post("/confirm-college-email", summary="Confirm college email verification")
async def confirm_college_email_verification(
    student_id: str,
    token: str,
    db: Session = Depends(get_db),
):
    """
    Confirm college email verification using the token sent to the student's college email.
    """
    success = CollegeVerificationService.verify_token(student_id, token, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    return {
        "success": True,
        "message": "College email verified successfully.",
    }


# Student Profile Endpoints (Phase 5)


@router.get(
    "/me/profile",
    response_model=StudentProfileResponse,
    summary="Get current student's profile",
)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get the current authenticated student's profile with full details.
    Requires STUDENT role.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint",
        )

    student = StudentService.get_student_by_user_id(current_user.id, db)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    profile = StudentService.get_student_profile(student.id, db)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return profile


@router.get(
    "/{student_id}/profile",
    response_model=StudentProfileResponse,
    summary="Get student profile by ID",
)
async def get_student_profile(
    student_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a student's profile by ID.
    Public endpoint - returns limited info for verified students.
    """
    profile = StudentService.get_student_profile(student_id, db)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return profile


@router.patch(
    "/me/profile",
    response_model=StudentProfileResponse,
    summary="Update current student's profile",
)
async def update_my_profile(
    student_data: StudentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update the current authenticated student's profile.
    Requires STUDENT role.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint",
        )

    student = StudentService.get_student_by_user_id(current_user.id, db)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    updated_student = StudentService.update_student(student.id, student_data, db)
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return StudentService.get_student_profile(updated_student.id, db)


@router.get(
    "/me/verification",
    response_model=StudentVerificationResponse,
    summary="Get current student's verification status",
)
async def get_my_verification_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get the current authenticated student's verification status.
    Requires STUDENT role.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint",
        )

    student = StudentService.get_student_by_user_id(current_user.id, db)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return StudentVerificationResponse(
        id=student.id,
        verification_status=student.verification_status.value,
        verified_at=student.verified_at,
        is_email_verified=current_user.is_email_verified,
    )


# Student Favorites Endpoints


@router.get(
    "/me/favorites",
    response_model=FavoriteListResponse,
    summary="Get saved favorite businesses",
)
async def get_my_favorites(
    latitude: Optional[float] = Query(
        None, ge=-90, le=90, description="User latitude for distance calculation"
    ),
    longitude: Optional[float] = Query(
        None, ge=-180, le=180, description="User longitude for distance calculation"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get current student's saved/favorited businesses with distance and open status.
    Requires authentication.
    """
    items, total = FavoriteService.list_user_favorites(
        user_id=current_user.id,
        db=db,
        user_lat=latitude,
        user_lng=longitude,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return FavoriteListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/me/favorites/{business_id}",
    response_model=FavoriteActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save business to favorites",
)
async def add_business_to_favorites(
    business_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Save a business to current student's favorites list.
    Requires authentication.
    """
    try:
        FavoriteService.add_favorite(
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
        message="Business added to favorites",
        is_favorite=True,
    )


@router.delete(
    "/me/favorites/{business_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove business from favorites",
)
async def remove_business_from_favorites(
    business_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Remove a business from student's favorites list.
    Requires authentication.
    """
    success = FavoriteService.remove_favorite(
        user_id=current_user.id,
        business_id=business_id,
        db=db,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found in favorites",
        )
    return None


# Admin endpoints for student management (to be expanded in Phase 15)


@router.get("", response_model=list[StudentResponse], summary="List students (admin)")
async def list_students(
    college_id: UUID | None = None,
    campus_id: UUID | None = None,
    verification_status: VerificationStatus | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """
    List students with optional filters.
    Admin only endpoint - requires ADMIN role.
    """
    # TODO: Add admin authorization check
    skip = (page - 1) * page_size
    students = StudentService.list_students(
        db=db,
        college_id=college_id,
        campus_id=campus_id,
        verification_status=verification_status,
        skip=skip,
        limit=page_size,
    )
    return students
