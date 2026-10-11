"""Unit tests for FavoriteService."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.business import Business
from app.models.favorite import Favorite
from app.services.favorite_service import FavoriteService


def test_add_favorite_success():
    """Test adding a business to favorites creates a Favorite entry."""
    mock_db = MagicMock()
    user_id = uuid4()
    business_id = uuid4()

    business = Business(id=business_id, name="Campus Mess")

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is Favorite:
            m.filter.return_value.first.return_value = None  # Not yet favorited
        return m

    mock_db.query.side_effect = query_side_effect

    fav = FavoriteService.add_favorite(user_id, business_id, mock_db)
    assert fav.user_id == user_id
    assert fav.business_id == business_id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_add_favorite_idempotent():
    """Test adding an already favorited business returns existing record without duplicate insertion."""
    mock_db = MagicMock()
    user_id = uuid4()
    business_id = uuid4()

    business = Business(id=business_id, name="Campus Mess")
    existing_fav = Favorite(user_id=user_id, business_id=business_id)

    def query_side_effect(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is Favorite:
            m.filter.return_value.first.return_value = existing_fav
        return m

    mock_db.query.side_effect = query_side_effect

    fav = FavoriteService.add_favorite(user_id, business_id, mock_db)
    assert fav == existing_fav
    mock_db.add.assert_not_called()


def test_add_favorite_business_not_found():
    """Test adding non-existent business raises ValueError."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Business not found"):
        FavoriteService.add_favorite(uuid4(), uuid4(), mock_db)


def test_remove_favorite_success():
    """Test removing existing favorite deletes it from database."""
    mock_db = MagicMock()
    user_id = uuid4()
    business_id = uuid4()

    fav = Favorite(user_id=user_id, business_id=business_id)
    mock_db.query.return_value.filter.return_value.first.return_value = fav

    success = FavoriteService.remove_favorite(user_id, business_id, mock_db)
    assert success is True
    mock_db.delete.assert_called_once_with(fav)
    mock_db.commit.assert_called_once()


def test_remove_favorite_nonexistent():
    """Test removing a favorite that does not exist returns False."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    success = FavoriteService.remove_favorite(uuid4(), uuid4(), mock_db)
    assert success is False


def test_is_favorite():
    """Test is_favorite returns correct boolean state."""
    mock_db = MagicMock()
    user_id = uuid4()
    business_id = uuid4()

    fav = Favorite(user_id=user_id, business_id=business_id)
    mock_db.query.return_value.filter.return_value.first.return_value = fav

    assert FavoriteService.is_favorite(user_id, business_id, mock_db) is True

    mock_db.query.return_value.filter.return_value.first.return_value = None
    assert FavoriteService.is_favorite(user_id, business_id, mock_db) is False


def test_toggle_favorite():
    """Test toggle_favorite switches state."""
    mock_db = MagicMock()
    user_id = uuid4()
    business_id = uuid4()
    business = Business(id=business_id, name="Campus Cafe")

    # First toggle: not favorited -> add favorite
    fav = Favorite(user_id=user_id, business_id=business_id)

    def query_side_effect_add(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is Favorite:
            m.filter.return_value.first.return_value = None
        return m

    mock_db.query.side_effect = query_side_effect_add
    is_fav, msg = FavoriteService.toggle_favorite(user_id, business_id, mock_db)
    assert is_fav is True
    assert msg == "Business added to favorites"

    # Second toggle: favorited -> remove favorite
    def query_side_effect_remove(*args, **kwargs):
        m = MagicMock()
        model = args[0] if args else None
        if model is Business:
            m.filter.return_value.first.return_value = business
        elif model is Favorite:
            m.filter.return_value.first.return_value = fav
        return m

    mock_db.query.side_effect = query_side_effect_remove
    is_fav, msg = FavoriteService.toggle_favorite(user_id, business_id, mock_db)
    assert is_fav is False
    assert msg == "Business removed from favorites"


def test_calculate_distance():
    """Test Haversine distance calculation."""
    # Pune MIT AOE approx (18.6750, 73.8900) to nearby spot (18.6790, 73.8920)
    dist = FavoriteService.calculate_distance(18.6750, 73.8900, 18.6790, 73.8920)
    assert dist > 400
    assert dist < 600
