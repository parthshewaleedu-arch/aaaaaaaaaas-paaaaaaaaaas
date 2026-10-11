"""Unit tests for Maps and Campuses API endpoints."""

from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.campus import Campus
from app.schemas.campus import (
    CampusCollegeInfo,
    CampusResponse,
)
from app.schemas.map import (
    BoundingBox,
    CampusMapResponse,
    DirectionsResponse,
    MapMarkerResponse,
)
from app.services.campus_service import CampusService
from app.services.map_service import MapService


def _dummy_campus_response(campus_id=None):
    c_id = campus_id or uuid4()
    return CampusResponse(
        id=c_id,
        college_id=uuid4(),
        name="Alandi Main Campus",
        address="Alandi, Pune",
        latitude=18.6750,
        longitude=73.8980,
        radius_meters=3000,
        college=CampusCollegeInfo(id=uuid4(), name="MIT AOE", short_name="MITAOE"),
        business_count=10,
    )


def test_list_campuses_endpoint():
    """Test public GET /api/v1/campuses."""
    mock_db = MagicMock()
    campus_resp = _dummy_campus_response()

    original_list = CampusService.list_campuses
    CampusService.list_campuses = staticmethod(
        lambda *args, **kwargs: ([campus_resp], 1)
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get("/api/v1/campuses")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Alandi Main Campus"
    finally:
        CampusService.list_campuses = original_list
        app.dependency_overrides.clear()


def test_get_campus_details_endpoint():
    """Test public GET /api/v1/campuses/{id}."""
    mock_db = MagicMock()
    campus_resp = _dummy_campus_response()

    original_get = CampusService.get_campus_by_id
    CampusService.get_campus_by_id = staticmethod(lambda *args, **kwargs: campus_resp)

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/campuses/{campus_resp.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(campus_resp.id)
        assert data["name"] == "Alandi Main Campus"
    finally:
        CampusService.get_campus_by_id = original_get
        app.dependency_overrides.clear()


def test_get_campus_map_endpoint():
    """Test public GET /api/v1/campuses/{id}/map."""
    mock_db = MagicMock()
    campus_resp = _dummy_campus_response()
    marker = MapMarkerResponse(
        id=uuid4(),
        name="Campus Bakery",
        latitude=18.6752,
        longitude=73.8982,
        distance_meters=35,
        student_discount=True,
    )
    map_payload = CampusMapResponse(
        campus=campus_resp,
        bounding_box=BoundingBox(
            min_lat=18.65, max_lat=18.70, min_lng=73.85, max_lng=73.95
        ),
        markers=[marker],
        total_markers=1,
    )

    original_map = CampusService.get_campus_map_data
    CampusService.get_campus_map_data = staticmethod(
        lambda *args, **kwargs: map_payload
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(f"/api/v1/campuses/{campus_resp.id}/map")
        assert response.status_code == 200
        data = response.json()
        assert data["total_markers"] == 1
        assert data["markers"][0]["name"] == "Campus Bakery"
        assert data["bounding_box"]["min_lat"] == 18.65
    finally:
        CampusService.get_campus_map_data = original_map
        app.dependency_overrides.clear()


def test_get_map_markers_bounding_box_endpoint():
    """Test GET /api/v1/map/markers with bounding box viewport parameters."""
    mock_db = MagicMock()
    marker = MapMarkerResponse(
        id=uuid4(),
        name="Alandi South Cafe",
        latitude=18.676,
        longitude=73.899,
        student_discount=False,
    )

    original_bbox = MapService.get_markers_in_bounding_box
    MapService.get_markers_in_bounding_box = staticmethod(
        lambda *args, **kwargs: [marker]
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(
            "/api/v1/map/markers?min_lat=18.67&min_lng=73.89&max_lat=18.68&max_lng=73.90"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Alandi South Cafe"
        assert data["bounding_box"]["min_lat"] == 18.67
    finally:
        MapService.get_markers_in_bounding_box = original_bbox
        app.dependency_overrides.clear()


def test_get_map_markers_radius_endpoint():
    """Test GET /api/v1/map/markers with latitude, longitude and radius parameters."""
    mock_db = MagicMock()
    marker = MapMarkerResponse(
        id=uuid4(),
        name="Nearby Juice Center",
        latitude=18.6751,
        longitude=73.8981,
        distance_meters=20,
        student_discount=True,
    )

    original_radius = MapService.get_markers_within_radius
    MapService.get_markers_within_radius = staticmethod(
        lambda *args, **kwargs: [marker]
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(
            "/api/v1/map/markers?latitude=18.6750&longitude=73.8980&radius_meters=1500"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Nearby Juice Center"
    finally:
        MapService.get_markers_within_radius = original_radius
        app.dependency_overrides.clear()


def test_get_map_markers_missing_params_rejected():
    """Test GET /api/v1/map/markers without bounding box or center coordinates raises 400."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get("/api/v1/map/markers")
        assert response.status_code == 400
        data = response.json()
        assert "either" in data["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_get_campuses_map_overlays_endpoint():
    """Test GET /api/v1/map/campuses returns campus overlay items."""
    mock_db = MagicMock()
    campus = Campus(
        id=uuid4(),
        name="Alandi Campus",
        address="Pune",
        latitude=18.6750,
        longitude=73.8980,
        radius_meters=3000,
    )
    mock_db.query.return_value.all.return_value = [campus]

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get("/api/v1/map/campuses")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alandi Campus"
        assert data[0]["radius_meters"] == 3000
    finally:
        app.dependency_overrides.clear()


def test_get_business_directions_endpoint():
    """Test GET /api/v1/businesses/{id}/directions returns route calculations and Google Maps link."""
    mock_db = MagicMock()
    biz_id = uuid4()
    dir_resp = DirectionsResponse(
        business_id=biz_id,
        business_name="College Canteen",
        destination_latitude=18.6760,
        destination_longitude=73.8990,
        user_latitude=18.6750,
        user_longitude=73.8980,
        distance_meters=150,
        distance_km=0.15,
        estimated_walking_minutes=2,
        compass_bearing="NE",
        bearing_degrees=42.5,
        google_maps_url=(
            "https://www.google.com/maps/dir/?api=1&origin=18.675,73.898&destination=18.676,73.899&travelmode=walking"
        ),
    )

    original_directions = MapService.get_directions
    MapService.get_directions = staticmethod(lambda *args, **kwargs: dir_resp)

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        client = TestClient(app)
        response = client.get(
            f"/api/v1/businesses/{biz_id}/directions?user_lat=18.6750&user_lng=73.8980"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["business_id"] == str(biz_id)
        assert data["distance_meters"] == 150
        assert data["estimated_walking_minutes"] == 2
        assert data["compass_bearing"] == "NE"
        assert "travelmode=walking" in data["google_maps_url"]
    finally:
        MapService.get_directions = original_directions
        app.dependency_overrides.clear()
