"""Admin Endpoints.

REST API routes for platform administration: dashboard metrics,
user management, business approvals, review moderation, report resolutions,
and immutable audit trails. All endpoints require ADMIN role privileges.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin_user
from app.core.database import get_db
from app.models.business import BusinessStatus, BusinessVerificationStatus
from app.models.user import User, UserRole, UserStatus
from app.schemas.admin import (
    AdminAuditLogAdminInfo,
    AdminAuditLogItemResponse,
    AdminAuditLogListResponse,
    AdminBusinessListResponse,
    AdminBusinessStatusUpdateRequest,
    AdminBusinessVerifyRequest,
    AdminDashboardResponse,
    AdminReviewListResponse,
    AdminReviewModerateRequest,
    AdminUserListResponse,
    AdminUserStatusUpdateRequest,
)
from app.schemas.report import (
    AdminReportListResponse,
    ReportResolveRequest,
)
from app.services.admin_service import AdminService
from app.services.report_service import ReportService

router = APIRouter()


# -------------------------------------------------------------------------
# Dashboard Metrics
# -------------------------------------------------------------------------
@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
    summary="Get admin dashboard metrics",
)
def get_dashboard(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve platform KPI metrics: students, businesses, reviews, and pending moderation reports."""
    metrics = AdminService.get_dashboard_metrics(db=db)
    return AdminDashboardResponse(data=metrics)


# -------------------------------------------------------------------------
# User Management
# -------------------------------------------------------------------------
@router.get(
    "/users",
    response_model=AdminUserListResponse,
    summary="List users with filters",
)
def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    status: Optional[UserStatus] = Query(None, description="Filter by user status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve paginated user accounts with optional role, status, and keyword filtering."""
    skip = (page - 1) * limit
    users, total = AdminService.list_users(
        db=db,
        role=role,
        status_filter=status,
        search=search,
        skip=skip,
        limit=limit,
    )
    return AdminUserListResponse(
        data=users,
        total=total,
        page=page,
        limit=limit,
    )


@router.patch(
    "/users/{id}",
    response_model=dict,
    summary="Update user status",
)
def update_user_status(
    id: UUID,
    body: AdminUserStatusUpdateRequest,
    request: Request,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Suspend, activate, or deactivate a user account with audit logging."""
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated_user = AdminService.update_user_status(
        db=db,
        user_id=id,
        admin_id=current_admin.id,
        new_status=body.status,
        reason=body.reason,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    return {
        "success": True,
        "data": updated_user.model_dump(),
        "message": "User status updated successfully",
    }


# -------------------------------------------------------------------------
# Business Management
# -------------------------------------------------------------------------
@router.get(
    "/businesses",
    response_model=AdminBusinessListResponse,
    summary="List businesses for admin oversight",
)
def list_businesses(
    status: Optional[BusinessStatus] = Query(
        None, description="Filter by listing status"
    ),
    verification_status: Optional[BusinessVerificationStatus] = Query(
        None, description="Filter by verification state"
    ),
    campus_id: Optional[UUID] = Query(None, description="Filter by campus"),
    search: Optional[str] = Query(None, description="Search by business name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve businesses for verification, moderation, and auditing."""
    skip = (page - 1) * limit
    items, total = AdminService.list_businesses(
        db=db,
        status_filter=status,
        verification_status=verification_status,
        campus_id=campus_id,
        search=search,
        skip=skip,
        limit=limit,
    )
    return AdminBusinessListResponse(
        data=items,
        total=total,
        page=page,
        limit=limit,
    )


@router.patch(
    "/businesses/{id}/verify",
    response_model=dict,
    summary="Approve or reject business verification",
)
def verify_business(
    id: UUID,
    body: AdminBusinessVerifyRequest,
    request: Request,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Approve (VERIFIED) or reject a merchant's business verification application."""
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = AdminService.verify_business(
        db=db,
        business_id=id,
        admin_id=current_admin.id,
        action=body.action,
        reason=body.reason,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    return {
        "success": True,
        "data": updated.model_dump(),
        "message": f"Business verification {body.action.lower()}d successfully",
    }


@router.patch(
    "/businesses/{id}/status",
    response_model=dict,
    summary="Update business listing status",
)
def update_business_status(
    id: UUID,
    body: AdminBusinessStatusUpdateRequest,
    request: Request,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Suspend, activate, or remove a business listing with audit logging."""
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = AdminService.update_business_status(
        db=db,
        business_id=id,
        admin_id=current_admin.id,
        new_status=body.status,
        reason=body.reason,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    return {
        "success": True,
        "data": updated.model_dump(),
        "message": "Business status updated successfully",
    }


# -------------------------------------------------------------------------
# Review Moderation
# -------------------------------------------------------------------------
@router.get(
    "/reviews",
    response_model=AdminReviewListResponse,
    summary="List reviews for moderation",
)
def list_reviews(
    business_id: Optional[UUID] = Query(None, description="Filter by business"),
    reported_only: bool = Query(
        False, description="Filter reviews with active reports only"
    ),
    status: Optional[str] = Query(
        None, description="Filter by review status (ACTIVE, REMOVED)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Query reviews with moderation statuses and reported counters."""
    skip = (page - 1) * limit
    items, total = AdminService.list_reviews(
        db=db,
        business_id=business_id,
        reported_only=reported_only,
        status_filter=status,
        skip=skip,
        limit=limit,
    )
    return AdminReviewListResponse(
        data=items,
        total=total,
        page=page,
        limit=limit,
    )


@router.patch(
    "/reviews/{id}/moderate",
    response_model=dict,
    summary="Moderate review",
)
def moderate_review(
    id: UUID,
    body: AdminReviewModerateRequest,
    request: Request,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Moderate review: keep (dismiss reports) or remove (soft-delete, recalculate business rating)."""
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = AdminService.moderate_review(
        db=db,
        review_id=id,
        admin_id=current_admin.id,
        action=body.action,
        reason=body.reason,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    return {
        "success": True,
        "data": updated.model_dump(),
        "message": f"Review {body.action.lower()}ed successfully",
    }


# -------------------------------------------------------------------------
# Report Moderation Queue
# -------------------------------------------------------------------------
@router.get(
    "/reports",
    response_model=AdminReportListResponse,
    summary="Get all reports (reviews and businesses)",
)
def list_reports(
    type: Optional[str] = Query(
        None, description="Filter by report type: BUSINESS or REVIEW"
    ),
    status: Optional[str] = Query(
        None, description="Filter by report status: PENDING, RESOLVED, etc."
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve unified moderation queue encompassing both business and review complaints."""
    skip = (page - 1) * limit
    items, total = ReportService.list_reports(
        db=db,
        report_type=type,
        status_filter=status,
        skip=skip,
        limit=limit,
    )
    return AdminReportListResponse(
        data=items,
        total=total,
        page=page,
        limit=limit,
    )


@router.patch(
    "/reports/{id}",
    response_model=dict,
    summary="Resolve report",
)
def resolve_report(
    id: UUID,
    body: ReportResolveRequest,
    request: Request,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Resolve or dismiss a moderation report with audit trail recording."""
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = ReportService.resolve_report(
        db=db,
        report_id=id,
        admin_id=current_admin.id,
        target_status=body.status,
        resolution_notes=body.resolution_notes,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    return {
        "success": True,
        "data": updated.model_dump(),
        "message": f"Report marked as {body.status.value}",
    }


# -------------------------------------------------------------------------
# Audit Logs
# -------------------------------------------------------------------------
@router.get(
    "/audit-logs",
    response_model=AdminAuditLogListResponse,
    summary="View admin action audit trail",
)
def list_audit_logs(
    admin_id: Optional[UUID] = Query(None, description="Filter by admin user ID"),
    entity_type: Optional[str] = Query(
        None, description="Filter by entity type (user, business, review)"
    ),
    action: Optional[str] = Query(None, description="Filter by action code"),
    from_date: Optional[datetime] = Query(None, description="Filter from timestamp"),
    to_date: Optional[datetime] = Query(None, description="Filter to timestamp"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Query immutable administrator and moderation audit trail."""
    skip = (page - 1) * limit
    logs, total = AdminService.list_audit_logs(
        db=db,
        admin_id=admin_id,
        entity_type=entity_type,
        action=action,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit,
    )

    items = [
        AdminAuditLogItemResponse(
            id=log.id,
            admin=(
                AdminAuditLogAdminInfo(
                    id=log.admin.id,
                    email=log.admin.email,
                )
                if log.admin
                else None
            ),
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            old_data=log.old_data,
            new_data=log.new_data,
            reason=log.reason,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return AdminAuditLogListResponse(
        data=items,
        total=total,
        page=page,
        limit=limit,
    )
