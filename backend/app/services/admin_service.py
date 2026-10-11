"""Admin Service.

Handles administrative operations: platform metrics aggregation,
user management, business approvals and status changes, review moderation,
and immutable audit log recording.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional, Tuple
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.audit_log import AuditLog
from app.models.business import (
    Business,
    BusinessStatus,
    BusinessVerificationStatus,
)
from app.models.business_report import BusinessReport, BusinessReportStatus
from app.models.review import Review, ReviewStatus
from app.models.review_report import ReviewReport, ReviewReportStatus
from app.models.student import Student, VerificationStatus
from app.models.user import User, UserRole, UserStatus
from app.schemas.admin import (
    AdminBusinessItemResponse,
    AdminBusinessMetrics,
    AdminDashboardData,
    AdminReportMetrics,
    AdminReviewItemResponse,
    AdminReviewMetrics,
    AdminStudentMetrics,
    AdminUserItemResponse,
)
from app.services.review_service import ReviewService


class AdminService:
    """Service providing core administration, dashboard aggregation, and moderation capabilities."""

    @classmethod
    def record_audit_log(
        cls,
        db: Session,
        admin_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID,
        old_data: Optional[Any] = None,
        new_data: Optional[Any] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create and persist an immutable audit trail entry."""
        log = AuditLog(
            id=uuid4(),
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_data=old_data,
            new_data=new_data,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @classmethod
    def get_dashboard_metrics(cls, db: Session) -> AdminDashboardData:
        """Aggregate high-level platform health, user, listing, and moderation metrics."""
        now = datetime.now(timezone.utc)
        first_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

        # 1. Student metrics
        total_students = db.query(Student).count()
        verified_students = (
            db.query(Student)
            .filter(Student.verification_status == VerificationStatus.VERIFIED)
            .count()
        )
        pending_students = (
            db.query(Student)
            .filter(Student.verification_status == VerificationStatus.PENDING)
            .count()
        )

        # 2. Business metrics
        total_businesses = (
            db.query(Business).filter(Business.deleted_at.is_(None)).count()
        )
        active_businesses = (
            db.query(Business)
            .filter(
                Business.status == BusinessStatus.ACTIVE,
                Business.deleted_at.is_(None),
            )
            .count()
        )
        pending_businesses = (
            db.query(Business)
            .filter(
                Business.verification_status == BusinessVerificationStatus.PENDING,
                Business.deleted_at.is_(None),
            )
            .count()
        )
        verified_businesses = (
            db.query(Business)
            .filter(
                Business.verification_status == BusinessVerificationStatus.VERIFIED,
                Business.deleted_at.is_(None),
            )
            .count()
        )

        # 3. Review metrics
        total_reviews = db.query(Review).filter(Review.deleted_at.is_(None)).count()
        month_reviews = (
            db.query(Review)
            .filter(
                Review.deleted_at.is_(None),
                Review.created_at >= first_of_month,
            )
            .count()
        )

        # 4. Reports metrics
        pending_review_reports = (
            db.query(ReviewReport)
            .filter(ReviewReport.status == ReviewReportStatus.PENDING)
            .count()
        )
        pending_business_reports = (
            db.query(BusinessReport)
            .filter(BusinessReport.status == BusinessReportStatus.PENDING)
            .count()
        )

        return AdminDashboardData(
            students=AdminStudentMetrics(
                total=total_students,
                verified=verified_students,
                pending_verification=pending_students,
            ),
            businesses=AdminBusinessMetrics(
                total=total_businesses,
                active=active_businesses,
                pending_verification=pending_businesses,
                verified=verified_businesses,
            ),
            reviews=AdminReviewMetrics(
                total=total_reviews,
                this_month=month_reviews,
            ),
            reports=AdminReportMetrics(
                pending_review_reports=pending_review_reports,
                pending_business_reports=pending_business_reports,
            ),
        )

    @classmethod
    def list_users(
        cls,
        db: Session,
        role: Optional[UserRole] = None,
        status_filter: Optional[UserStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[AdminUserItemResponse], int]:
        """Query and paginate users with administrative filters."""
        query = db.query(User)

        if role:
            query = query.filter(User.role == role)
        if status_filter:
            query = query.filter(User.status == status_filter)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(User.email.ilike(search_pattern))

        total = query.count()
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

        user_items = [
            AdminUserItemResponse(
                id=u.id,
                email=u.email,
                phone=u.phone,
                role=u.role,
                status=u.status,
                is_email_verified=bool(u.is_email_verified),
                is_phone_verified=bool(u.is_phone_verified),
                created_at=u.created_at,
                last_login_at=u.last_login_at,
            )
            for u in users
        ]
        return user_items, total

    @classmethod
    def update_user_status(
        cls,
        db: Session,
        user_id: UUID,
        admin_id: UUID,
        new_status: UserStatus,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AdminUserItemResponse:
        """Change a user's account status and record an audit log."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        old_status = (
            user.status.value if hasattr(user.status, "value") else str(user.status)
        )
        new_status_val = (
            new_status.value if hasattr(new_status, "value") else str(new_status)
        )

        user.status = new_status
        db.commit()
        db.refresh(user)

        cls.record_audit_log(
            db=db,
            admin_id=admin_id,
            action="UPDATE_USER_STATUS",
            entity_type="user",
            entity_id=user.id,
            old_data={"status": old_status},
            new_data={"status": new_status_val},
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return AdminUserItemResponse(
            id=user.id,
            email=user.email,
            phone=user.phone,
            role=user.role,
            status=user.status,
            is_email_verified=bool(user.is_email_verified),
            is_phone_verified=bool(user.is_phone_verified),
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )

    @classmethod
    def list_businesses(
        cls,
        db: Session,
        status_filter: Optional[BusinessStatus] = None,
        verification_status: Optional[BusinessVerificationStatus] = None,
        campus_id: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[AdminBusinessItemResponse], int]:
        """List businesses for admin monitoring, verification and moderation."""
        query = (
            db.query(Business)
            .options(
                joinedload(Business.owner),
                joinedload(Business.campus),
            )
            .filter(Business.deleted_at.is_(None))
        )

        if status_filter:
            query = query.filter(Business.status == status_filter)
        if verification_status:
            query = query.filter(Business.verification_status == verification_status)
        if campus_id:
            query = query.filter(Business.campus_id == campus_id)
        if search:
            query = query.filter(Business.name.ilike(f"%{search.strip()}%"))

        total = query.count()
        businesses = (
            query.order_by(Business.created_at.desc()).offset(skip).limit(limit).all()
        )

        items = [
            AdminBusinessItemResponse(
                id=b.id,
                name=b.name,
                owner_id=b.owner_id,
                owner_email=b.owner.email if b.owner else None,
                campus_id=b.campus_id,
                campus_name=b.campus.name if b.campus else None,
                status=b.status,
                verification_status=b.verification_status,
                average_rating=float(b.average_rating)
                if b.average_rating is not None
                else None,
                review_count=b.review_count or 0,
                created_at=b.created_at,
                verified_at=b.verified_at,
                rejection_reason=b.rejection_reason,
            )
            for b in businesses
        ]
        return items, total

    @classmethod
    def verify_business(
        cls,
        db: Session,
        business_id: UUID,
        admin_id: UUID,
        action: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AdminBusinessItemResponse:
        """Approve or reject a merchant verification request."""
        business = (
            db.query(Business)
            .options(joinedload(Business.owner), joinedload(Business.campus))
            .filter(Business.id == business_id, Business.deleted_at.is_(None))
            .first()
        )
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        old_data = {
            "status": business.status.value
            if hasattr(business.status, "value")
            else str(business.status),
            "verification_status": (
                business.verification_status.value
                if hasattr(business.verification_status, "value")
                else str(business.verification_status)
            ),
        }

        if action.upper() == "APPROVE":
            business.verification_status = BusinessVerificationStatus.VERIFIED
            business.verified_at = datetime.now(timezone.utc)
            business.verification_notes = reason
            business.rejection_reason = None
            if business.status == BusinessStatus.PENDING:
                business.status = BusinessStatus.ACTIVE
        else:  # REJECT
            business.verification_status = BusinessVerificationStatus.UNVERIFIED
            business.rejection_reason = reason

        db.commit()
        db.refresh(business)

        new_data = {
            "status": business.status.value
            if hasattr(business.status, "value")
            else str(business.status),
            "verification_status": (
                business.verification_status.value
                if hasattr(business.verification_status, "value")
                else str(business.verification_status)
            ),
        }

        cls.record_audit_log(
            db=db,
            admin_id=admin_id,
            action=f"VERIFY_BUSINESS_{action.upper()}",
            entity_type="business",
            entity_id=business.id,
            old_data=old_data,
            new_data=new_data,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return AdminBusinessItemResponse(
            id=business.id,
            name=business.name,
            owner_id=business.owner_id,
            owner_email=business.owner.email if business.owner else None,
            campus_id=business.campus_id,
            campus_name=business.campus.name if business.campus else None,
            status=business.status,
            verification_status=business.verification_status,
            average_rating=float(business.average_rating)
            if business.average_rating is not None
            else None,
            review_count=business.review_count or 0,
            created_at=business.created_at,
            verified_at=business.verified_at,
            rejection_reason=business.rejection_reason,
        )

    @classmethod
    def update_business_status(
        cls,
        db: Session,
        business_id: UUID,
        admin_id: UUID,
        new_status: BusinessStatus,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AdminBusinessItemResponse:
        """Suspend, activate, or remove a business listing."""
        business = (
            db.query(Business)
            .options(joinedload(Business.owner), joinedload(Business.campus))
            .filter(Business.id == business_id)
            .first()
        )
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        old_status = (
            business.status.value
            if hasattr(business.status, "value")
            else str(business.status)
        )
        new_status_val = (
            new_status.value if hasattr(new_status, "value") else str(new_status)
        )

        business.status = new_status
        if new_status == BusinessStatus.REMOVED:
            business.deleted_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(business)

        cls.record_audit_log(
            db=db,
            admin_id=admin_id,
            action="UPDATE_BUSINESS_STATUS",
            entity_type="business",
            entity_id=business.id,
            old_data={"status": old_status},
            new_data={"status": new_status_val},
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return AdminBusinessItemResponse(
            id=business.id,
            name=business.name,
            owner_id=business.owner_id,
            owner_email=business.owner.email if business.owner else None,
            campus_id=business.campus_id,
            campus_name=business.campus.name if business.campus else None,
            status=business.status,
            verification_status=business.verification_status,
            average_rating=float(business.average_rating)
            if business.average_rating is not None
            else None,
            review_count=business.review_count or 0,
            created_at=business.created_at,
            verified_at=business.verified_at,
            rejection_reason=business.rejection_reason,
        )

    @classmethod
    def list_reviews(
        cls,
        db: Session,
        business_id: Optional[UUID] = None,
        reported_only: bool = False,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[AdminReviewItemResponse], int]:
        """List reviews for moderation with report counts."""
        query = (
            db.query(
                Review,
                func.count(ReviewReport.id).label("report_count"),
            )
            .outerjoin(ReviewReport, ReviewReport.review_id == Review.id)
            .options(
                joinedload(Review.business),
                joinedload(Review.user),
            )
            .group_by(Review.id)
        )

        if business_id:
            query = query.filter(Review.business_id == business_id)
        if status_filter:
            query = query.filter(Review.status == status_filter)
        if reported_only:
            query = query.having(func.count(ReviewReport.id) > 0)

        total = query.count()
        results = (
            query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
        )

        items = []
        for r, rep_count in results:
            items.append(
                AdminReviewItemResponse(
                    id=r.id,
                    business_id=r.business_id,
                    business_name=r.business.name if r.business else None,
                    user_id=r.user_id,
                    user_email=r.user.email if r.user else None,
                    overall_rating=float(r.overall_rating),
                    review_text=r.review_text,
                    verification_level=(
                        r.verification_level.value
                        if hasattr(r.verification_level, "value")
                        else str(r.verification_level)
                    ),
                    status=r.status.value
                    if hasattr(r.status, "value")
                    else str(r.status),
                    helpful_count=r.helpful_count or 0,
                    report_count=rep_count,
                    created_at=r.created_at,
                    deleted_at=r.deleted_at,
                )
            )
        return items, total

    @classmethod
    def moderate_review(
        cls,
        db: Session,
        review_id: UUID,
        admin_id: UUID,
        action: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AdminReviewItemResponse:
        """Moderate a review: remove or keep, resolving filed reports and recalculating ratings."""
        review = (
            db.query(Review)
            .options(joinedload(Review.business), joinedload(Review.user))
            .filter(Review.id == review_id)
            .first()
        )
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )

        old_status = (
            review.status.value
            if hasattr(review.status, "value")
            else str(review.status)
        )
        now = datetime.now(timezone.utc)

        if action.upper() == "REMOVE":
            review.status = ReviewStatus.REMOVED
            review.deleted_at = now
            # Recalculate business average rating and review count
            ReviewService.recalculate_business_ratings(review.business_id, db)

            # Auto-resolve pending review reports
            pending_reports = (
                db.query(ReviewReport)
                .filter(
                    ReviewReport.review_id == review.id,
                    ReviewReport.status == ReviewReportStatus.PENDING,
                )
                .all()
            )
            for rep in pending_reports:
                rep.status = ReviewReportStatus.RESOLVED
                rep.resolved_at = now
                rep.resolved_by = admin_id
                rep.resolution_notes = (
                    f"Auto-resolved: Review removed ({reason or 'Moderation action'})"
                )
        else:  # KEEP
            review.status = ReviewStatus.ACTIVE
            review.deleted_at = None
            ReviewService.recalculate_business_ratings(review.business_id, db)

            # Dismiss pending review reports
            pending_reports = (
                db.query(ReviewReport)
                .filter(
                    ReviewReport.review_id == review.id,
                    ReviewReport.status == ReviewReportStatus.PENDING,
                )
                .all()
            )
            for rep in pending_reports:
                rep.status = ReviewReportStatus.DISMISSED
                rep.resolved_at = now
                rep.resolved_by = admin_id
                rep.resolution_notes = (
                    f"Dismissed: Review kept ({reason or 'Deemed appropriate'})"
                )

        db.commit()
        db.refresh(review)

        cls.record_audit_log(
            db=db,
            admin_id=admin_id,
            action=f"MODERATE_REVIEW_{action.upper()}",
            entity_type="review",
            entity_id=review.id,
            old_data={"status": old_status},
            new_data={
                "status": review.status.value
                if hasattr(review.status, "value")
                else str(review.status)
            },
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        rep_count = (
            db.query(ReviewReport).filter(ReviewReport.review_id == review.id).count()
        )

        return AdminReviewItemResponse(
            id=review.id,
            business_id=review.business_id,
            business_name=review.business.name if review.business else None,
            user_id=review.user_id,
            user_email=review.user.email if review.user else None,
            overall_rating=float(review.overall_rating),
            review_text=review.review_text,
            verification_level=(
                review.verification_level.value
                if hasattr(review.verification_level, "value")
                else str(review.verification_level)
            ),
            status=review.status.value
            if hasattr(review.status, "value")
            else str(review.status),
            helpful_count=review.helpful_count or 0,
            report_count=rep_count,
            created_at=review.created_at,
            deleted_at=review.deleted_at,
        )

    @classmethod
    def list_audit_logs(
        cls,
        db: Session,
        admin_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[AuditLog], int]:
        """Fetch audit log records with filtering and pagination."""
        query = db.query(AuditLog).options(joinedload(AuditLog.admin))

        if admin_id:
            query = query.filter(AuditLog.admin_id == admin_id)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if action:
            query = query.filter(AuditLog.action == action)
        if from_date:
            query = query.filter(AuditLog.created_at >= from_date)
        if to_date:
            query = query.filter(AuditLog.created_at <= to_date)

        total = query.count()
        logs = (
            query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        )
        return logs, total
