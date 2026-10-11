"""Unit tests for ReportService."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.business import Business
from app.models.business_report import (
    BusinessReport,
    BusinessReportReason,
    BusinessReportStatus,
)
from app.models.review import Review
from app.models.review_report import (
    ReviewReport,
    ReviewReportReason,
    ReviewReportStatus,
)
from app.models.user import User
from app.schemas.report import BusinessReportCreate
from app.services.report_service import ReportService


def test_create_business_report_success():
    """Test successfully filing a report against a business listing."""
    mock_db = MagicMock()
    biz_id = uuid4()
    owner_id = uuid4()
    reporter_id = uuid4()

    biz = Business(
        id=biz_id,
        name="Campus Xerox & Print",
        owner_id=owner_id,
        deleted_at=None,
    )

    mock_db.query.return_value.filter.return_value.first.return_value = biz

    req = BusinessReportCreate(
        reason=BusinessReportReason.INCORRECT_PRICES,
        description="Listed prices on menu do not match actual store prices",
    )

    report_resp = ReportService.create_business_report(
        business_id=biz_id,
        reported_by=reporter_id,
        data=req,
        db=mock_db,
    )

    assert report_resp.business_id == biz_id
    assert report_resp.business_name == "Campus Xerox & Print"
    assert report_resp.reported_by == reporter_id
    assert report_resp.reason == "INCORRECT_PRICES"
    assert report_resp.status == "PENDING"
    assert mock_db.add.called
    assert mock_db.commit.called


def test_create_business_report_nonexistent_business_fails():
    """Test filing a report against a missing business raises 404."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    req = BusinessReportCreate(
        reason=BusinessReportReason.FAKE_LISTING,
        description="Does not exist on campus",
    )

    with pytest.raises(HTTPException) as exc:
        ReportService.create_business_report(
            business_id=uuid4(),
            reported_by=uuid4(),
            data=req,
            db=mock_db,
        )
    assert exc.value.status_code == 404


def test_create_business_report_owner_cannot_report_own_business():
    """Test that a business owner is rejected with 400 when reporting their own listing."""
    mock_db = MagicMock()
    biz_id = uuid4()
    owner_id = uuid4()

    biz = Business(
        id=biz_id,
        name="Owner Cafe",
        owner_id=owner_id,
        deleted_at=None,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = biz

    req = BusinessReportCreate(
        reason=BusinessReportReason.OTHER,
        description="Self report test",
    )

    with pytest.raises(HTTPException) as exc:
        ReportService.create_business_report(
            business_id=biz_id,
            reported_by=owner_id,
            data=req,
            db=mock_db,
        )
    assert exc.value.status_code == 400


def test_get_business_report_success():
    """Test retrieving a business report by ID."""
    mock_db = MagicMock()
    rep_id = uuid4()
    biz_id = uuid4()

    biz = Business(id=biz_id, name="Campus Cafe")
    report = BusinessReport(
        id=rep_id,
        business_id=biz_id,
        reported_by=uuid4(),
        reason=BusinessReportReason.CLOSED_BUSINESS,
        description="Shop is permanently closed",
        status=BusinessReportStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
    report.business = biz

    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        report
    )

    res = ReportService.get_business_report(rep_id, mock_db)
    assert res.id == rep_id
    assert res.business_name == "Campus Cafe"
    assert res.reason == "CLOSED_BUSINESS"


def test_list_reports_combines_and_sorts_correctly():
    """Test unified queue combines and sorts business and review moderation reports."""
    mock_db = MagicMock()

    biz = Business(id=uuid4(), name="Stationery Store")
    reporter1 = User(id=uuid4(), email="student1@college.edu")

    b_report = BusinessReport(
        id=uuid4(),
        business_id=biz.id,
        reported_by=reporter1.id,
        reason=BusinessReportReason.FAKE_LISTING,
        description="Fake address",
        status=BusinessReportStatus.PENDING,
        created_at=datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc),
    )
    b_report.business = biz
    b_report.reporter = reporter1

    rev = Review(id=uuid4(), review_text="Spam review text content")
    reporter2 = User(id=uuid4(), email="student2@college.edu")

    r_report = ReviewReport(
        id=uuid4(),
        review_id=rev.id,
        reported_by=reporter2.id,
        reason=ReviewReportReason.SPAM,
        description="Spam link in review",
        status=ReviewReportStatus.PENDING,
        created_at=datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc),
    )
    r_report.review = rev
    r_report.reporter = reporter2

    query_mock = MagicMock()
    query_mock.options.return_value.all.side_effect = [[b_report], [r_report]]
    mock_db.query.return_value = query_mock

    items, total = ReportService.list_reports(db=mock_db, skip=0, limit=10)

    assert total == 2
    assert len(items) == 2
    # Newer report (review report from Sept 11) should be first
    assert items[0].report_type == "REVIEW"
    assert items[0].reporter_email == "student2@college.edu"
    assert items[1].report_type == "BUSINESS"
    assert items[1].target_title == "Stationery Store"


def test_resolve_business_report_success():
    """Test resolving a business report updates status, resolved_by, and logs audit."""
    mock_db = MagicMock()
    admin_id = uuid4()
    rep_id = uuid4()
    biz_id = uuid4()

    biz = Business(id=biz_id, name="Book Store")
    reporter = User(id=uuid4(), email="reporter@college.edu")

    biz_report = BusinessReport(
        id=rep_id,
        business_id=biz_id,
        reported_by=reporter.id,
        reason=BusinessReportReason.INCORRECT_INFORMATION,
        description="Hours are wrong",
        status=BusinessReportStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
    biz_report.business = biz
    biz_report.reporter = reporter

    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        biz_report
    )

    resolved_item = ReportService.resolve_report(
        db=mock_db,
        report_id=rep_id,
        admin_id=admin_id,
        target_status=BusinessReportStatus.RESOLVED,
        resolution_notes="Contacted merchant and corrected information",
    )

    assert resolved_item.id == rep_id
    assert resolved_item.status == "RESOLVED"
    assert resolved_item.resolved_by == admin_id
    assert (
        resolved_item.resolution_notes == "Contacted merchant and corrected information"
    )
    assert mock_db.commit.called
