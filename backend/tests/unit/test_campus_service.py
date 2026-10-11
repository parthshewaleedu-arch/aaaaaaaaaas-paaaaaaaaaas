"""Unit tests for CampusService."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.business import Business, BusinessStatus
from app.models.campus import Campus
from app.models.college import College
from app.services.campus_service import CampusService


def test_list_campuses_success():
    """Test listing all campuses returns populated college and business counts."""
    mock_db = MagicMock()
    campus_id = uuid4()
    college_id = uuid4()

    college = College(
        id=college_id, name="MIT Academy of Engineering", short_name="MITAOE"
    )
    campus = Campus(
        id=campus_id,
        college_id=college_id,
        college=college,
        name="Alandi Main Campus",
        address="Alandi, Pune",
        latitude=18.6750,
        longitude=73.8980,
        radius_meters=3000,
    )

    query_mock = MagicMock()
    query_mock.options.return_value = query_mock
    query_mock.count.return_value = 1
    query_mock.offset.return_value.limit.return_value.all.return_value = [campus]

    count_mock = MagicMock()
    count_mock.filter.return_value.count.return_value = 14

    def side_effect(*args, **kwargs):
        if args and args[0] is Campus:
            return query_mock
        return count_mock

    mock_db.query.side_effect = side_effect

    campuses, total = CampusService.list_campuses(mock_db)
    assert total == 1
    assert len(campuses) == 1
    assert campuses[0].name == "Alandi Main Campus"
    assert campuses[0].college.short_name == "MITAOE"
    assert campuses[0].business_count == 14


def test_get_campus_by_id_success():
    """Test retrieving campus by ID."""
    mock_db = MagicMock()
    campus_id = uuid4()
    college_id = uuid4()

    college = College(
        id=college_id, name="MIT Academy of Engineering", short_name="MITAOE"
    )
    campus = Campus(
        id=campus_id,
        college_id=college_id,
        college=college,
        name="Alandi Main Campus",
        address="Alandi, Pune",
        latitude=18.6750,
        longitude=73.8980,
        radius_meters=3000,
    )

    query_mock = MagicMock()
    query_mock.options.return_value.filter.return_value.first.return_value = campus

    count_mock = MagicMock()
    count_mock.filter.return_value.count.return_value = 5

    def side_effect(*args, **kwargs):
        if args and args[0] is Campus:
            return query_mock
        return count_mock

    mock_db.query.side_effect = side_effect

    res = CampusService.get_campus_by_id(campus_id, mock_db)
    assert res.id == campus_id
    assert res.name == "Alandi Main Campus"
    assert res.business_count == 5


def test_get_campus_by_id_not_found():
    """Test non-existent campus raises 404."""
    mock_db = MagicMock()
    campus_id = uuid4()
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        None
    )

    with pytest.raises(HTTPException) as exc:
        CampusService.get_campus_by_id(campus_id, mock_db)
    assert exc.value.status_code == 404


def test_get_campus_map_data_success():
    """Test retrieving map view payload for campus returns bounding box and markers."""
    mock_db = MagicMock()
    campus_id = uuid4()
    college_id = uuid4()
    biz_id = uuid4()

    college = College(id=college_id, name="MIT College", short_name="MIT")
    campus = Campus(
        id=campus_id,
        college_id=college_id,
        college=college,
        name="Main Campus",
        address="Campus Road",
        latitude=18.6750,
        longitude=73.8980,
        radius_meters=2000,
    )

    business = Business(
        id=biz_id,
        campus_id=campus_id,
        name="Campus Fast Food",
        latitude=18.6760,
        longitude=73.8990,
        status=BusinessStatus.ACTIVE,
        average_rating=4.5,
        student_discount=True,
    )
    business.categories = []
    business.hours = []

    def side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Campus:
            m.options.return_value.filter.return_value.first.return_value = campus
        elif model is Business:
            m.options.return_value.filter.return_value.all.return_value = [business]
            m.filter.return_value.count.return_value = 1
        return m

    mock_db.query.side_effect = side_effect

    map_data = CampusService.get_campus_map_data(campus_id, mock_db)
    assert map_data.campus.id == campus_id
    assert map_data.bounding_box.min_lat < map_data.campus.latitude
    assert map_data.bounding_box.max_lat > map_data.campus.latitude
    assert map_data.total_markers == 1
    assert map_data.markers[0].name == "Campus Fast Food"
    assert map_data.markers[0].student_discount is True
