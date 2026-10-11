"""Unit tests for search and filtering features in BusinessService."""

from unittest.mock import MagicMock
from uuid import uuid4

from app.models.business import Business, BusinessStatus
from app.services.business_service import BusinessService


def test_haversine_distance_calculation():
    """Test Great-Circle distance calculation between coordinates."""
    # MIT AOE gate (approx 18.6756, 73.8890) to Alandi center (approx 18.6780, 73.8960)
    lat1, lon1 = 18.6756, 73.8890
    lat2, lon2 = 18.6780, 73.8960

    dist = BusinessService.calculate_distance_meters(lat1, lon1, lat2, lon2)
    # Should be approximately 750-850 meters
    assert 700 <= dist <= 900

    # Same location should be 0 distance
    assert BusinessService.calculate_distance_meters(18.67, 73.88, 18.67, 73.88) == 0


def test_distance_calculation_attached_to_businesses():
    """Test that distance_meters is computed and added to returned business items."""
    mock_db = MagicMock()

    b1 = Business(
        id=uuid4(),
        name="Nearby Cafe",
        latitude=18.6760,
        longitude=73.8895,
        status=BusinessStatus.ACTIVE,
    )
    b2 = Business(
        id=uuid4(),
        name="Far Restaurant",
        latitude=18.6900,
        longitude=73.9100,
        status=BusinessStatus.ACTIVE,
    )

    mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
        b1,
        b2,
    ]

    user_lat, user_lon = 18.6756, 73.8890
    results = BusinessService.list_businesses(
        db=mock_db,
        latitude=user_lat,
        longitude=user_lon,
        sort="distance",
    )

    assert len(results) == 2
    assert hasattr(results[0], "distance_meters")
    assert hasattr(results[1], "distance_meters")
    assert results[0].distance_meters < results[1].distance_meters
    assert results[0].name == "Nearby Cafe"


def test_search_by_keyword_filters_query():
    """Test that search query filters both name and description."""
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value

    BusinessService.list_businesses(
        db=mock_db,
        search="sharma mess",
    )

    # Verify query.filter was called for the search term
    assert mock_query.filter.called


def test_filter_by_student_discount_and_price_level():
    """Test filtering by student discount and price level."""
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value = mock_query

    BusinessService.list_businesses(
        db=mock_db,
        student_discount=True,
        price_level="₹₹",
        min_rating=4.0,
    )

    # Query filter should be called for discount, price, and rating
    assert mock_query.filter.call_count >= 3
