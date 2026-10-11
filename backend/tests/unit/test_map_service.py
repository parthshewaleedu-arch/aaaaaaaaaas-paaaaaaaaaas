"""Unit tests for MapService."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.business import Business, BusinessStatus
from app.services.map_service import MapService


def test_calculate_distance_haversine():
    """Test Haversine distance between two known geographic points in Pune."""
    # Point A: MITAOE Alandi (18.6750, 73.8980)
    # Point B: Alandi Temple (18.6780, 73.8995)
    dist = MapService.calculate_distance(18.6750, 73.8980, 18.6780, 73.8995)
    # ~365 meters
    assert 300 < dist < 450


def test_calculate_bearing_cardinal_directions():
    """Test compass bearing calculations and cardinal direction mapping."""
    # Due North: (0, 0) to (1, 0)
    deg_n, card_n = MapService.calculate_bearing(0.0, 0.0, 1.0, 0.0)
    assert card_n == "N"
    assert deg_n == 0.0

    # Due East: (0, 0) to (0, 1)
    deg_e, card_e = MapService.calculate_bearing(0.0, 0.0, 0.0, 1.0)
    assert card_e == "E"
    assert 89.0 <= deg_e <= 91.0

    # North-East: (0, 0) to (1, 1)
    deg_ne, card_ne = MapService.calculate_bearing(0.0, 0.0, 1.0, 1.0)
    assert card_ne == "NE"
    assert 40.0 <= deg_ne <= 50.0

    # Due South: (1, 0) to (0, 0)
    deg_s, card_s = MapService.calculate_bearing(1.0, 0.0, 0.0, 0.0)
    assert card_s == "S"
    assert 179.0 <= deg_s <= 181.0


def test_calculate_walking_minutes():
    """Test walking duration estimate."""
    # 400 meters at 4.8 km/h (80 m/min) -> 5 mins
    mins = MapService.calculate_walking_minutes(400)
    assert mins == 5

    # 50 meters -> minimum 1 min
    mins_short = MapService.calculate_walking_minutes(50)
    assert mins_short == 1


def test_get_markers_in_bounding_box():
    """Test querying markers within a bounding box."""
    mock_db = MagicMock()
    biz = Business(
        id=uuid4(),
        name="Alandi Chai",
        latitude=18.6755,
        longitude=73.8985,
        status=BusinessStatus.ACTIVE,
        average_rating=4.2,
        student_discount=False,
    )
    biz.categories = []
    biz.hours = []

    mock_db.query.return_value.options.return_value.filter.return_value.limit.return_value.all.return_value = [
        biz
    ]

    markers = MapService.get_markers_in_bounding_box(
        min_lat=18.6700,
        min_lng=73.8900,
        max_lat=18.6800,
        max_lng=73.9000,
        db=mock_db,
    )
    assert len(markers) == 1
    assert markers[0].name == "Alandi Chai"
    assert markers[0].latitude == 18.6755


def test_get_markers_within_radius():
    """Test querying markers within a circular radius."""
    mock_db = MagicMock()
    biz1 = Business(
        id=uuid4(),
        name="Close Cafe",
        latitude=18.6752,
        longitude=73.8981,
        status=BusinessStatus.ACTIVE,
    )
    biz1.categories = []
    biz1.hours = []

    mock_db.query.return_value.options.return_value.filter.return_value.limit.return_value.all.return_value = [
        biz1
    ]

    markers = MapService.get_markers_within_radius(
        latitude=18.6750,
        longitude=73.8980,
        radius_meters=1000,
        db=mock_db,
    )
    assert len(markers) == 1
    assert markers[0].name == "Close Cafe"
    assert markers[0].distance_meters is not None
    assert markers[0].distance_meters < 1000


def test_get_directions_success():
    """Test get_directions returns distance, walking time, bearing, and Google Maps link."""
    mock_db = MagicMock()
    biz_id = uuid4()
    biz = Business(
        id=biz_id,
        name="Destination Restaurant",
        latitude=18.6790,
        longitude=73.9000,
        status=BusinessStatus.ACTIVE,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = biz

    user_lat = 18.6750
    user_lng = 73.8980

    directions = MapService.get_directions(
        business_id=biz_id,
        user_lat=user_lat,
        user_lng=user_lng,
        db=mock_db,
    )

    assert directions.business_id == biz_id
    assert directions.business_name == "Destination Restaurant"
    assert directions.distance_meters > 0
    assert directions.estimated_walking_minutes >= 1
    assert directions.compass_bearing in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    assert "https://www.google.com/maps/dir/?api=1" in directions.google_maps_url
    assert "travelmode=walking" in directions.google_maps_url


def test_get_directions_business_not_found():
    """Test directions for non-existent business raises 404."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        MapService.get_directions(
            business_id=uuid4(),
            user_lat=18.0,
            user_lng=73.0,
            db=mock_db,
        )
    assert exc.value.status_code == 404
