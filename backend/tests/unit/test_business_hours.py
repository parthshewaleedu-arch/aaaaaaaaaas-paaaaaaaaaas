"""Unit tests for business operating hours schedule and open status calculation."""

from datetime import datetime, time, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.business import Business
from app.models.business_hours import BusinessHours
from app.schemas.business import BusinessHoursItem
from app.services.business_service import BusinessService


def test_set_business_hours_valid():
    """Test owner setting full weekly schedule."""
    mock_db = MagicMock()
    business_id = uuid4()
    business = Business(id=business_id, name="Campus Cafe")
    mock_db.query.return_value.filter.return_value.first.return_value = business

    schedule_data = [
        BusinessHoursItem(
            day_of_week=0, open_time=time(8, 0), close_time=time(22, 0), is_closed=False
        ),
        BusinessHoursItem(
            day_of_week=1, open_time=time(8, 0), close_time=time(22, 0), is_closed=False
        ),
        BusinessHoursItem(
            day_of_week=2, open_time=time(8, 0), close_time=time(22, 0), is_closed=False
        ),
        BusinessHoursItem(
            day_of_week=3, open_time=time(8, 0), close_time=time(22, 0), is_closed=False
        ),
        BusinessHoursItem(
            day_of_week=4, open_time=time(8, 0), close_time=time(22, 0), is_closed=False
        ),
        BusinessHoursItem(
            day_of_week=5, open_time=time(8, 0), close_time=time(22, 0), is_closed=False
        ),
        BusinessHoursItem(
            day_of_week=6, open_time=None, close_time=None, is_closed=True
        ),
    ]

    result = BusinessService.set_business_hours(business_id, schedule_data, mock_db)

    assert len(result) == 7
    mock_db.commit.assert_called_once()
    assert result[0].day_of_week == 0
    assert result[0].is_closed is False
    assert result[6].day_of_week == 6
    assert result[6].is_closed is True


def test_set_business_hours_invalid_day_raises():
    """Test day_of_week outside 0-6 raises ValueError."""
    mock_db = MagicMock()
    business_id = uuid4()
    business = Business(id=business_id, name="Campus Cafe")
    mock_db.query.return_value.filter.return_value.first.return_value = business

    schedule_data = [
        {
            "day_of_week": 7,
            "open_time": time(8, 0),
            "close_time": time(20, 0),
            "is_closed": False,
        }
    ]

    with pytest.raises(ValueError, match="Invalid day_of_week"):
        BusinessService.set_business_hours(business_id, schedule_data, mock_db)


def test_set_business_hours_missing_time_when_not_closed_raises():
    """Test open_time or close_time None when is_closed=False raises ValueError."""
    mock_db = MagicMock()
    business_id = uuid4()
    business = Business(id=business_id, name="Campus Cafe")
    mock_db.query.return_value.filter.return_value.first.return_value = business

    schedule_data = [
        BusinessHoursItem(
            day_of_week=1, open_time=None, close_time=None, is_closed=False
        )
    ]

    with pytest.raises(ValueError, match="Open and close times required"):
        BusinessService.set_business_hours(business_id, schedule_data, mock_db)


def test_calculate_open_status_open_now():
    """Test business is open during active operating hours."""
    # Day 1 is Monday. Let's fix time to Monday at 14:30
    monday_230pm = datetime(
        2026, 9, 21, 14, 30, tzinfo=timezone.utc
    )  # Sep 21 2026 is Monday (day 1)

    hours = [
        BusinessHours(
            day_of_week=1, open_time=time(9, 0), close_time=time(22, 0), is_closed=False
        ),
        BusinessHours(
            day_of_week=2, open_time=time(9, 0), close_time=time(22, 0), is_closed=False
        ),
    ]

    is_open, status_text = BusinessService.calculate_open_status(
        hours, now=monday_230pm
    )
    assert is_open is True
    assert status_text == "Open until 10:00 PM"


def test_calculate_open_status_before_opening():
    """Test business is closed before opening time."""
    monday_8am = datetime(2026, 9, 21, 8, 0, tzinfo=timezone.utc)  # Monday 8:00 AM

    hours = [
        BusinessHours(
            day_of_week=1,
            open_time=time(9, 30),
            close_time=time(22, 0),
            is_closed=False,
        ),
    ]

    is_open, status_text = BusinessService.calculate_open_status(hours, now=monday_8am)
    assert is_open is False
    assert status_text == "Closed • Opens at 9:30 AM"


def test_calculate_open_status_after_closing_shows_next_day():
    """Test business closed after hours shows next open day."""
    monday_11pm = datetime(2026, 9, 21, 23, 0, tzinfo=timezone.utc)  # Monday 11:00 PM

    hours = [
        BusinessHours(
            day_of_week=1, open_time=time(9, 0), close_time=time(22, 0), is_closed=False
        ),
        BusinessHours(
            day_of_week=2, open_time=time(9, 0), close_time=time(22, 0), is_closed=False
        ),
    ]

    is_open, status_text = BusinessService.calculate_open_status(hours, now=monday_11pm)
    assert is_open is False
    assert "Opens tomorrow at 9:00 AM" in status_text


def test_calculate_open_status_empty_hours():
    """Test empty schedule returns not available."""
    is_open, status_text = BusinessService.calculate_open_status([])
    assert is_open is False
    assert status_text == "Hours not available"


def test_calculate_open_status_overnight_shift():
    """Test overnight shift open calculation (e.g. 20:00 to 02:00)."""
    monday_11pm = datetime(2026, 9, 21, 23, 0, tzinfo=timezone.utc)  # Monday 11:00 PM
    hours = [
        BusinessHours(
            day_of_week=1, open_time=time(20, 0), close_time=time(2, 0), is_closed=False
        ),
    ]
    is_open, status_text = BusinessService.calculate_open_status(hours, now=monday_11pm)
    assert is_open is True
    assert status_text == "Open until 2:00 AM"
