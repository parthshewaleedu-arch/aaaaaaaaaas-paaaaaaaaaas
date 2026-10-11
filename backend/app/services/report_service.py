"""Report Service.

Manages business moderation reports and provides unified administration
resolution queues for both business and review moderation reports.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.sanitizer import sanitize_text
from app.models.business import Business
from app.models.business_report import BusinessReport, BusinessReportStatus
from app.models.review_report import ReviewReport, ReviewReportStatus
from app.schemas.report import (
    AdminReportItemResponse,
    BusinessReportCreate,
    BusinessReportResponse,
)
from app.services.admin_service import AdminService


class ReportService:
    """Service handling moderation reporting workflows and administrative resolutions."""

    @classmethod
    def create_business_report(
        cls,
        business_id: UUID,
        reported_by: UUID,
        data: BusinessReportCreate,
        db: Session,
    ) -> BusinessReportResponse:
        """Submit a moderation report against a business listing."""
        business = (
            db.query(Business)
            .filter(Business.id == business_id, Business.deleted_at.is_(None))
            .first()
        )
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found",
            )

        if business.owner_id == reported_by:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business owners cannot report their own business",
            )

        report = BusinessReport(
            id=uuid4(),
            business_id=business_id,
            reported_by=reported_by,
            reason=data.reason,
            description=sanitize_text(data.description.strip()),
            status=BusinessReportStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return BusinessReportResponse(
            id=report.id,
            business_id=report.business_id,
            business_name=business.name,
            reported_by=report.reported_by,
            reason=report.reason.value
            if hasattr(report.reason, "value")
            else str(report.reason),
            description=report.description,
            status=report.status.value
            if hasattr(report.status, "value")
            else str(report.status),
            created_at=report.created_at,
            resolved_at=report.resolved_at,
            resolved_by=report.resolved_by,
            resolution_notes=report.resolution_notes,
        )

    @classmethod
    def get_business_report(
        cls,
        report_id: UUID,
        db: Session,
    ) -> BusinessReportResponse:
        """Retrieve a specific business moderation report."""
        report = (
            db.query(BusinessReport)
            .options(joinedload(BusinessReport.business))
            .filter(BusinessReport.id == report_id)
            .first()
        )
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business report not found",
            )

        return BusinessReportResponse(
            id=report.id,
            business_id=report.business_id,
            business_name=report.business.name if report.business else None,
            reported_by=report.reported_by,
            reason=report.reason.value
            if hasattr(report.reason, "value")
            else str(report.reason),
            description=report.description,
            status=report.status.value
            if hasattr(report.status, "value")
            else str(report.status),
            created_at=report.created_at,
            resolved_at=report.resolved_at,
            resolved_by=report.resolved_by,
            resolution_notes=report.resolution_notes,
        )

    @classmethod
    def list_reports(
        cls,
        db: Session,
        report_type: Optional[str] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[AdminReportItemResponse], int]:
        """Query and combine business and review moderation reports into a unified queue."""
        items: List[AdminReportItemResponse] = []

        query_business = report_type is None or report_type.upper() == "BUSINESS"
        query_review = report_type is None or report_type.upper() == "REVIEW"

        if query_business:
            b_query = db.query(BusinessReport).options(
                joinedload(BusinessReport.business),
                joinedload(BusinessReport.reporter),
            )
            if status_filter:
                b_query = b_query.filter(BusinessReport.status == status_filter)
            biz_reports = b_query.all()

            for b in biz_reports:
                items.append(
                    AdminReportItemResponse(
                        id=b.id,
                        report_type="BUSINESS",
                        target_id=b.business_id,
                        target_title=b.business.name if b.business else None,
                        reported_by=b.reported_by,
                        reporter_email=b.reporter.email if b.reporter else None,
                        reason=b.reason.value
                        if hasattr(b.reason, "value")
                        else str(b.reason),
                        description=b.description,
                        status=b.status.value
                        if hasattr(b.status, "value")
                        else str(b.status),
                        created_at=b.created_at,
                        resolved_at=b.resolved_at,
                        resolved_by=b.resolved_by,
                        resolution_notes=b.resolution_notes,
                    )
                )

        if query_review:
            r_query = db.query(ReviewReport).options(
                joinedload(ReviewReport.review),
                joinedload(ReviewReport.reporter),
            )
            if status_filter:
                r_query = r_query.filter(ReviewReport.status == status_filter)
            rev_reports = r_query.all()

            for r in rev_reports:
                review_text_snippet = (
                    r.review.review_text[:60] + "..."
                    if r.review
                    and r.review.review_text
                    and len(r.review.review_text) > 60
                    else (r.review.review_text if r.review else None)
                )
                items.append(
                    AdminReportItemResponse(
                        id=r.id,
                        report_type="REVIEW",
                        target_id=r.review_id,
                        target_title=review_text_snippet,
                        reported_by=r.reported_by,
                        reporter_email=r.reporter.email if r.reporter else None,
                        reason=r.reason.value
                        if hasattr(r.reason, "value")
                        else str(r.reason),
                        description=r.description,
                        status=r.status.value
                        if hasattr(r.status, "value")
                        else str(r.status),
                        created_at=r.created_at,
                        resolved_at=r.resolved_at,
                        resolved_by=r.resolved_by,
                        resolution_notes=r.resolution_notes,
                    )
                )

        # Sort combined queue by creation date descending
        items.sort(key=lambda x: x.created_at, reverse=True)
        total = len(items)
        end_idx = skip + limit
        paginated_items = items[skip:end_idx]

        return paginated_items, total

    @classmethod
    def resolve_report(
        cls,
        db: Session,
        report_id: UUID,
        admin_id: UUID,
        target_status: BusinessReportStatus,
        resolution_notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AdminReportItemResponse:
        """Resolve or dismiss a moderation report (business or review)."""
        now = datetime.now(timezone.utc)

        # 1. Check if it is a BusinessReport
        biz_report = (
            db.query(BusinessReport)
            .options(
                joinedload(BusinessReport.business),
                joinedload(BusinessReport.reporter),
            )
            .filter(BusinessReport.id == report_id)
            .first()
        )
        if biz_report:
            old_status = (
                biz_report.status.value
                if hasattr(biz_report.status, "value")
                else str(biz_report.status)
            )
            biz_report.status = target_status
            biz_report.resolved_at = now
            biz_report.resolved_by = admin_id
            biz_report.resolution_notes = resolution_notes
            db.commit()
            db.refresh(biz_report)

            AdminService.record_audit_log(
                db=db,
                admin_id=admin_id,
                action=f"RESOLVE_BUSINESS_REPORT_{target_status.value}",
                entity_type="business_report",
                entity_id=biz_report.id,
                old_data={"status": old_status},
                new_data={"status": target_status.value},
                reason=resolution_notes,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            return AdminReportItemResponse(
                id=biz_report.id,
                report_type="BUSINESS",
                target_id=biz_report.business_id,
                target_title=biz_report.business.name if biz_report.business else None,
                reported_by=biz_report.reported_by,
                reporter_email=biz_report.reporter.email
                if biz_report.reporter
                else None,
                reason=(
                    biz_report.reason.value
                    if hasattr(biz_report.reason, "value")
                    else str(biz_report.reason)
                ),
                description=biz_report.description,
                status=biz_report.status.value
                if hasattr(biz_report.status, "value")
                else str(biz_report.status),
                created_at=biz_report.created_at,
                resolved_at=biz_report.resolved_at,
                resolved_by=biz_report.resolved_by,
                resolution_notes=biz_report.resolution_notes,
            )

        # 2. Check if it is a ReviewReport
        rev_report = (
            db.query(ReviewReport)
            .options(
                joinedload(ReviewReport.review),
                joinedload(ReviewReport.reporter),
            )
            .filter(ReviewReport.id == report_id)
            .first()
        )
        if rev_report:
            old_status = (
                rev_report.status.value
                if hasattr(rev_report.status, "value")
                else str(rev_report.status)
            )
            rev_status = ReviewReportStatus(target_status.value)
            rev_report.status = rev_status
            rev_report.resolved_at = now
            rev_report.resolved_by = admin_id
            rev_report.resolution_notes = resolution_notes
            db.commit()
            db.refresh(rev_report)

            AdminService.record_audit_log(
                db=db,
                admin_id=admin_id,
                action=f"RESOLVE_REVIEW_REPORT_{target_status.value}",
                entity_type="review_report",
                entity_id=rev_report.id,
                old_data={"status": old_status},
                new_data={"status": target_status.value},
                reason=resolution_notes,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            snippet = (
                rev_report.review.review_text[:60] + "..."
                if rev_report.review
                and rev_report.review.review_text
                and len(rev_report.review.review_text) > 60
                else (rev_report.review.review_text if rev_report.review else None)
            )

            return AdminReportItemResponse(
                id=rev_report.id,
                report_type="REVIEW",
                target_id=rev_report.review_id,
                target_title=snippet,
                reported_by=rev_report.reported_by,
                reporter_email=rev_report.reporter.email
                if rev_report.reporter
                else None,
                reason=(
                    rev_report.reason.value
                    if hasattr(rev_report.reason, "value")
                    else str(rev_report.reason)
                ),
                description=rev_report.description,
                status=rev_report.status.value
                if hasattr(rev_report.status, "value")
                else str(rev_report.status),
                created_at=rev_report.created_at,
                resolved_at=rev_report.resolved_at,
                resolved_by=rev_report.resolved_by,
                resolution_notes=rev_report.resolution_notes,
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
