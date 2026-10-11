"""Unit tests for Review and Rating Dimension API endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_active_user
from app.core.database import get_db
from app.main import app
from app.models.business import Business, BusinessStatus, BusinessVerificationStatus
from app.models.rating_dimension import RatingDimension
from app.models.review import Review, ReviewStatus, VerificationLevel
from app.models.review_report import (
    ReviewReport,
    ReviewReportReason,
    ReviewReportStatus,
)
from app.models.review_response import ReviewResponse
from app.models.user import User, UserRole, UserStatus
from app.services.review_service import ReviewService


def test_get_business_reviews_endpoint_success():
    """Test public GET /api/v1/businesses/{id}/reviews returns reviews and rating breakdown."""
    business_id = uuid4()
    reviewer_id = uuid4()
    review_id = uuid4()

    mock_db = MagicMock()
    business = Business(
        id=business_id,
        name="Campus Eatery",
        status=BusinessStatus.ACTIVE,
        verification_status=BusinessVerificationStatus.VERIFIED,
    )

    review = Review(
        id=review_id,
        business_id=business_id,
        user_id=reviewer_id,
        overall_rating=5,
        review_text="Delicious food!",
        verification_level=VerificationLevel.VERIFIED_STUDENT,
        status=ReviewStatus.ACTIVE,
        helpful_count=3,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        ratings=[],
        photos=[],
        response=None,
    )

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        else:
            m.filter.return_value.first.return_value = None
        return m

    mock_db.query.side_effect = query_side_effect

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        original_list = ReviewService.list_reviews

        ReviewService.list_reviews = staticmethod(
            lambda *args, **kwargs: ([review], 1, {"Food Quality": 4.8})
        )

        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{business_id}/reviews")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "rating_breakdown" in data
        assert data["rating_breakdown"]["Food Quality"] == 4.8
        assert len(data["items"]) == 1
        assert data["items"][0]["overall_rating"] == 5
    finally:
        ReviewService.list_reviews = original_list
        app.dependency_overrides.clear()


def test_create_business_review_student_success():
    """Test authenticated student POST /api/v1/businesses/{id}/reviews."""
    business_id = uuid4()
    student_user_id = uuid4()
    dim_id = uuid4()

    mock_db = MagicMock()
    student_user = User(
        id=student_user_id,
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    created_review = Review(
        id=uuid4(),
        business_id=business_id,
        user_id=student_user_id,
        overall_rating=5,
        review_text="Excellent place to study and eat!",
        verification_level=VerificationLevel.VERIFIED_STUDENT,
        status=ReviewStatus.ACTIVE,
        helpful_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        ratings=[],
        photos=[],
        response=None,
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: student_user

    original_create = ReviewService.create_review
    ReviewService.create_review = staticmethod(lambda *args, **kwargs: created_review)
    try:
        client = TestClient(app)
        payload = {
            "overall_rating": 5,
            "review_text": "Excellent place to study and eat!",
            "ratings": [{"dimension_id": str(dim_id), "rating": 5}],
            "photo_urls": ["https://images.campus.edu/eatery.jpg"],
        }
        response = client.post(
            f"/api/v1/businesses/{business_id}/reviews",
            json=payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["overall_rating"] == 5
        assert data["review_text"] == "Excellent place to study and eat!"
    finally:
        ReviewService.create_review = original_create
        app.dependency_overrides.clear()


def test_create_business_review_unauthenticated():
    """Test unauthenticated POST /api/v1/businesses/{id}/reviews returns 401."""
    business_id = uuid4()
    client = TestClient(app)
    response = client.post(
        f"/api/v1/businesses/{business_id}/reviews",
        json={"overall_rating": 4, "review_text": "Nice"},
    )
    assert response.status_code == 401


def test_get_business_review_dimensions_endpoint():
    """Test public GET /api/v1/businesses/{id}/review-dimensions."""
    business_id = uuid4()
    dim_id = uuid4()
    mock_db = MagicMock()

    business = Business(id=business_id, name="Campus Mess")
    dimension = RatingDimension(
        id=dim_id,
        name="Hygiene",
        slug="hygiene",
        description="Cleanliness of dishes and kitchen",
        display_order=1,
    )

    mock_db.query.return_value.filter.return_value.first.return_value = business

    original_get_dims = ReviewService.get_dimensions_for_business
    ReviewService.get_dimensions_for_business = staticmethod(
        lambda b_id, db: [dimension]
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/businesses/{business_id}/review-dimensions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Hygiene"
        assert data[0]["slug"] == "hygiene"
    finally:
        ReviewService.get_dimensions_for_business = original_get_dims
        app.dependency_overrides.clear()


def test_get_review_by_id_endpoint_success():
    """Test public GET /api/v1/reviews/{id}."""
    review_id = uuid4()
    business_id = uuid4()
    user_id = uuid4()
    mock_db = MagicMock()

    review = Review(
        id=review_id,
        business_id=business_id,
        user_id=user_id,
        overall_rating=4,
        review_text="Pretty good experience",
        verification_level=VerificationLevel.VERIFIED_STUDENT,
        status=ReviewStatus.ACTIVE,
        helpful_count=2,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        ratings=[],
        photos=[],
        response=None,
    )

    original_get_review = ReviewService.get_review_by_id
    ReviewService.get_review_by_id = staticmethod(lambda r_id, db: review)

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/reviews/{review_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(review_id)
        assert data["overall_rating"] == 4
    finally:
        ReviewService.get_review_by_id = original_get_review
        app.dependency_overrides.clear()


def test_patch_review_owner_success():
    """Test student updating their own review via PATCH /api/v1/reviews/{id}."""
    review_id = uuid4()
    student_id = uuid4()
    mock_db = MagicMock()

    student_user = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    updated_review = Review(
        id=review_id,
        business_id=uuid4(),
        user_id=student_id,
        overall_rating=5,
        review_text="Updated review text",
        verification_level=VerificationLevel.VERIFIED_STUDENT,
        status=ReviewStatus.ACTIVE,
        helpful_count=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        ratings=[],
        photos=[],
        response=None,
    )

    original_update = ReviewService.update_review
    ReviewService.update_review = staticmethod(lambda *args, **kwargs: updated_review)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: student_user
    try:
        client = TestClient(app)
        response = client.patch(
            f"/api/v1/reviews/{review_id}",
            json={"overall_rating": 5, "review_text": "Updated review text"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["overall_rating"] == 5
        assert data["review_text"] == "Updated review text"
    finally:
        ReviewService.update_review = original_update
        app.dependency_overrides.clear()


def test_delete_review_owner_success():
    """Test student deleting their own review via DELETE /api/v1/reviews/{id}."""
    review_id = uuid4()
    student_id = uuid4()
    mock_db = MagicMock()

    student_user = User(id=student_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)

    original_delete = ReviewService.delete_review
    ReviewService.delete_review = staticmethod(lambda *args, **kwargs: True)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: student_user
    try:
        client = TestClient(app)
        response = client.delete(f"/api/v1/reviews/{review_id}")
        assert response.status_code == 204
    finally:
        ReviewService.delete_review = original_delete
        app.dependency_overrides.clear()


def test_respond_to_review_owner_endpoint_success():
    """Test business owner replying to a review via POST /api/v1/reviews/{id}/response."""
    review_id = uuid4()
    owner_id = uuid4()
    resp_id = uuid4()
    mock_db = MagicMock()

    owner_user = User(id=owner_id, role=UserRole.OWNER, status=UserStatus.ACTIVE)
    review_response = ReviewResponse(
        id=resp_id,
        review_id=review_id,
        owner_id=owner_id,
        response_text="Thank you for your valuable feedback!",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    original_respond = ReviewService.respond_to_review
    ReviewService.respond_to_review = staticmethod(
        lambda *args, **kwargs: review_response
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: owner_user
    try:
        client = TestClient(app)
        response = client.post(
            f"/api/v1/reviews/{review_id}/response",
            json={"response_text": "Thank you for your valuable feedback!"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(resp_id)
        assert data["response_text"] == "Thank you for your valuable feedback!"
    finally:
        ReviewService.respond_to_review = original_respond
        app.dependency_overrides.clear()


def test_report_review_endpoint_success():
    """Test user reporting a review via POST /api/v1/reviews/{id}/report."""
    review_id = uuid4()
    reporter_id = uuid4()
    report_id = uuid4()
    mock_db = MagicMock()

    user = User(id=reporter_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    review_report = ReviewReport(
        id=report_id,
        review_id=review_id,
        reported_by=reporter_id,
        reason=ReviewReportReason.SPAM,
        description="Spam link in review",
        status=ReviewReportStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )

    original_report = ReviewService.report_review
    ReviewService.report_review = staticmethod(lambda *args, **kwargs: review_report)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.post(
            f"/api/v1/reviews/{review_id}/report",
            json={"reason": "SPAM", "description": "Spam link in review"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(report_id)
        assert data["reason"] == "SPAM"
        assert data["status"] == "PENDING"
    finally:
        ReviewService.report_review = original_report
        app.dependency_overrides.clear()


def test_vote_helpful_endpoint_success():
    """Test user voting review helpful via POST /api/v1/reviews/{id}/helpful."""
    review_id = uuid4()
    user_id = uuid4()
    mock_db = MagicMock()

    user = User(id=user_id, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    review = Review(
        id=review_id,
        business_id=uuid4(),
        user_id=uuid4(),
        overall_rating=5,
        review_text="Super helpful place",
        verification_level=VerificationLevel.VERIFIED_STUDENT,
        status=ReviewStatus.ACTIVE,
        helpful_count=10,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        ratings=[],
        photos=[],
        response=None,
    )

    original_vote = ReviewService.vote_helpful
    ReviewService.vote_helpful = staticmethod(lambda *args, **kwargs: review)

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: user
    try:
        client = TestClient(app)
        response = client.post(f"/api/v1/reviews/{review_id}/helpful")
        assert response.status_code == 200
        data = response.json()
        assert data["helpful_count"] == 10
    finally:
        ReviewService.vote_helpful = original_vote
        app.dependency_overrides.clear()
