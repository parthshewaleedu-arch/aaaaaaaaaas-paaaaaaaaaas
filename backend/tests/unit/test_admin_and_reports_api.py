"""Unit tests for Admin and Reports REST API endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.main import app
from app.models.business import BusinessStatus, BusinessVerificationStatus
from app.models.business_report import BusinessReportReason, BusinessReportStatus
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
from app.schemas.report import (
    AdminReportItemResponse,
    BusinessReportResponse,
)
from app.services.admin_service import AdminService
from app.services.report_service import ReportService


def test_post_business_report_endpoint(monkeypatch):
    """Test POST /api/v1/businesses/{id}/report allows authenticated users to report a business."""
    mock_db = MagicMock()
    biz_id = uuid4()
    user_id = uuid4()

    mock_user = User(
        id=user_id,
        email="reporter@univ.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    report_resp = BusinessReportResponse(
        id=uuid4(),
        business_id=biz_id,
        business_name="College Canteen",
        reported_by=user_id,
        reason=BusinessReportReason.INCORRECT_PRICES.value,
        description="Menu prices are higher than listed",
        status=BusinessReportStatus.PENDING.value,
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        ReportService,
        "create_business_report",
        classmethod(lambda cls, *args, **kwargs: report_resp),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    try:
        client = TestClient(app)
        response = client.post(
            f"/api/v1/businesses/{biz_id}/report",
            json={
                "reason": "INCORRECT_PRICES",
                "description": "Menu prices are higher than listed",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["business_id"] == str(biz_id)
        assert data["reason"] == "INCORRECT_PRICES"
    finally:
        app.dependency_overrides.clear()


def test_get_admin_dashboard_endpoint_success(monkeypatch):
    """Test GET /api/v1/admin/dashboard returns metrics for admin user."""
    mock_db = MagicMock()
    admin_user = User(
        id=uuid4(),
        email="admin@aaspaas.com",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )

    dashboard_data = AdminDashboardData(
        students=AdminStudentMetrics(total=500, verified=450, pending_verification=50),
        businesses=AdminBusinessMetrics(
            total=120, active=100, pending_verification=15, verified=90
        ),
        reviews=AdminReviewMetrics(total=850, this_month=120),
        reports=AdminReportMetrics(
            pending_review_reports=8, pending_business_reports=3
        ),
    )

    monkeypatch.setattr(
        AdminService,
        "get_dashboard_metrics",
        classmethod(lambda cls, *args, **kwargs: dashboard_data),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.get("/api/v1/admin/dashboard")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["students"]["total"] == 500
        assert res["data"]["businesses"]["active"] == 100
    finally:
        app.dependency_overrides.clear()


def test_get_admin_dashboard_unauthorized_for_student():
    """Test that a non-admin user is rejected with 403 Forbidden."""
    mock_db = MagicMock()
    student_user = User(
        id=uuid4(),
        email="student@univ.edu",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: student_user

    try:
        client = TestClient(app)
        response = client.get("/api/v1/admin/dashboard")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_get_admin_users_endpoint(monkeypatch):
    """Test GET /api/v1/admin/users returns paginated users."""
    mock_db = MagicMock()
    admin_user = User(id=uuid4(), role=UserRole.ADMIN, status=UserStatus.ACTIVE)

    sample_user = AdminUserItemResponse(
        id=uuid4(),
        email="student@univ.edu",
        phone=None,
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
        is_phone_verified=False,
        created_at=datetime.now(timezone.utc),
        last_login_at=None,
    )

    monkeypatch.setattr(
        AdminService,
        "list_users",
        classmethod(lambda cls, *args, **kwargs: ([sample_user], 1)),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.get("/api/v1/admin/users?role=STUDENT&page=1&limit=20")
        assert response.status_code == 200
        res = response.json()
        assert res["total"] == 1
        assert res["data"][0]["email"] == "student@univ.edu"
    finally:
        app.dependency_overrides.clear()


def test_patch_admin_user_status_endpoint(monkeypatch):
    """Test PATCH /api/v1/admin/users/{id} updates user status."""
    mock_db = MagicMock()
    target_id = uuid4()
    admin_user = User(id=uuid4(), role=UserRole.ADMIN, status=UserStatus.ACTIVE)

    updated_user = AdminUserItemResponse(
        id=target_id,
        email="spammer@univ.edu",
        phone=None,
        role=UserRole.STUDENT,
        status=UserStatus.SUSPENDED,
        is_email_verified=True,
        is_phone_verified=False,
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        AdminService,
        "update_user_status",
        classmethod(lambda cls, *args, **kwargs: updated_user),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.patch(
            f"/api/v1/admin/users/{target_id}",
            json={"status": "SUSPENDED", "reason": "Spam activity"},
        )
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["status"] == "SUSPENDED"
    finally:
        app.dependency_overrides.clear()


def test_get_admin_businesses_endpoint(monkeypatch):
    """Test GET /api/v1/admin/businesses returns business listings for admin."""
    mock_db = MagicMock()
    admin_user = User(id=uuid4(), role=UserRole.ADMIN, status=UserStatus.ACTIVE)

    biz_item = AdminBusinessItemResponse(
        id=uuid4(),
        name="Chai Point",
        owner_id=uuid4(),
        owner_email="chai@owner.com",
        campus_id=uuid4(),
        campus_name="North Campus",
        status=BusinessStatus.ACTIVE,
        verification_status=BusinessVerificationStatus.VERIFIED,
        average_rating=4.3,
        review_count=18,
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        AdminService,
        "list_businesses",
        classmethod(lambda cls, *args, **kwargs: ([biz_item], 1)),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.get("/api/v1/admin/businesses?status=ACTIVE")
        assert response.status_code == 200
        res = response.json()
        assert res["total"] == 1
        assert res["data"][0]["name"] == "Chai Point"
    finally:
        app.dependency_overrides.clear()


def test_patch_admin_business_verify_endpoint(monkeypatch):
    """Test PATCH /api/v1/admin/businesses/{id}/verify approves verification."""
    mock_db = MagicMock()
    biz_id = uuid4()
    admin_user = User(id=uuid4(), role=UserRole.ADMIN, status=UserStatus.ACTIVE)

    verified_biz = AdminBusinessItemResponse(
        id=biz_id,
        name="Campus Xerox",
        owner_id=uuid4(),
        campus_id=uuid4(),
        status=BusinessStatus.ACTIVE,
        verification_status=BusinessVerificationStatus.VERIFIED,
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        AdminService,
        "verify_business",
        classmethod(lambda cls, *args, **kwargs: verified_biz),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.patch(
            f"/api/v1/admin/businesses/{biz_id}/verify",
            json={"action": "APPROVE", "reason": "All docs valid"},
        )
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["verification_status"] == "VERIFIED"
    finally:
        app.dependency_overrides.clear()


def test_patch_admin_reviews_moderate_endpoint(monkeypatch):
    """Test PATCH /api/v1/admin/reviews/{id}/moderate moderates a review."""
    mock_db = MagicMock()
    rev_id = uuid4()
    admin_user = User(id=uuid4(), role=UserRole.ADMIN, status=UserStatus.ACTIVE)

    moderated_review = AdminReviewItemResponse(
        id=rev_id,
        business_id=uuid4(),
        user_id=uuid4(),
        user_email="student@univ.edu",
        overall_rating=1.0,
        verification_level="VERIFIED_STUDENT",
        status="REMOVED",
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        AdminService,
        "moderate_review",
        classmethod(lambda cls, *args, **kwargs: moderated_review),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.patch(
            f"/api/v1/admin/reviews/{rev_id}/moderate",
            json={"action": "REMOVE", "reason": "Hate speech"},
        )
        assert response.status_code == 200
        res = response.json()
        assert res["data"]["status"] == "REMOVED"
    finally:
        app.dependency_overrides.clear()


def test_get_admin_reports_endpoint(monkeypatch):
    """Test GET /api/v1/admin/reports returns unified moderation complaints."""
    mock_db = MagicMock()
    admin_user = User(id=uuid4(), role=UserRole.ADMIN, status=UserStatus.ACTIVE)

    report_item = AdminReportItemResponse(
        id=uuid4(),
        report_type="BUSINESS",
        target_id=uuid4(),
        target_title="Fake Shop",
        reported_by=uuid4(),
        reason="FAKE_LISTING",
        status="PENDING",
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        ReportService,
        "list_reports",
        classmethod(lambda cls, *args, **kwargs: ([report_item], 1)),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.get("/api/v1/admin/reports")
        assert response.status_code == 200
        res = response.json()
        assert res["total"] == 1
        assert res["data"][0]["report_type"] == "BUSINESS"
    finally:
        app.dependency_overrides.clear()


def test_patch_admin_reports_resolve_endpoint(monkeypatch):
    """Test PATCH /api/v1/admin/reports/{id} resolves a report."""
    mock_db = MagicMock()
    rep_id = uuid4()
    admin_user = User(id=uuid4(), role=UserRole.ADMIN, status=UserStatus.ACTIVE)

    resolved_rep = AdminReportItemResponse(
        id=rep_id,
        report_type="BUSINESS",
        target_id=uuid4(),
        reported_by=uuid4(),
        reason="FAKE_LISTING",
        status="RESOLVED",
        resolution_notes="Closed listing",
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        ReportService,
        "resolve_report",
        classmethod(lambda cls, *args, **kwargs: resolved_rep),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.patch(
            f"/api/v1/admin/reports/{rep_id}",
            json={"status": "RESOLVED", "resolution_notes": "Closed listing"},
        )
        assert response.status_code == 200
        res = response.json()
        assert res["data"]["status"] == "RESOLVED"
    finally:
        app.dependency_overrides.clear()


def test_get_admin_audit_logs_endpoint(monkeypatch):
    """Test GET /api/v1/admin/audit-logs returns audit records."""
    mock_db = MagicMock()
    admin_user = User(id=uuid4(), role=UserRole.ADMIN, status=UserStatus.ACTIVE)

    mock_log = MagicMock()
    mock_log.id = uuid4()
    mock_log.action = "VERIFY_BUSINESS_APPROVE"
    mock_log.entity_type = "business"
    mock_log.entity_id = uuid4()
    mock_log.old_data = None
    mock_log.new_data = None
    mock_log.reason = "Approved"
    mock_log.ip_address = "127.0.0.1"
    mock_log.user_agent = "Browser"
    mock_log.created_at = datetime.now(timezone.utc)
    mock_log.admin = MagicMock(id=admin_user.id, email="admin@aaspaas.com")

    monkeypatch.setattr(
        AdminService,
        "list_audit_logs",
        classmethod(lambda cls, *args, **kwargs: ([mock_log], 1)),
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_admin_user] = lambda: admin_user

    try:
        client = TestClient(app)
        response = client.get("/api/v1/admin/audit-logs")
        assert response.status_code == 200
        res = response.json()
        assert res["total"] == 1
        assert res["data"][0]["action"] == "VERIFY_BUSINESS_APPROVE"
    finally:
        app.dependency_overrides.clear()
