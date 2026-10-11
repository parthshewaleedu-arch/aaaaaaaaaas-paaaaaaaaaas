"""Unit tests for ServiceService and price history tracking."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from app.models.business import Business
from app.models.service import Service
from app.models.service_price_history import ServicePriceHistory
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.service_service import ServiceService


def test_create_service_records_initial_price_history():
    """Test creating a service automatically creates an initial price history entry."""
    mock_db = MagicMock()
    business_id = uuid4()
    owner_id = uuid4()

    mock_db.query.return_value.filter.return_value.first.return_value = Business(
        id=business_id, name="Campus Mess"
    )

    service_data = ServiceCreate(
        name="Lunch Thali",
        description="2 Sabzi, 5 Roti, Rice, Dal",
        price=80.0,
        currency="INR",
        unit="plate",
    )

    service = ServiceService.create_service(
        business_id=business_id,
        service_data=service_data,
        db=mock_db,
        changed_by=owner_id,
    )

    assert service.name == "Lunch Thali"
    assert service.price == 80.0
    assert service.currency == "INR"
    assert service.unit == "plate"
    assert service.is_active is True

    # Check that both service and price history were added
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()


def test_update_service_price_change_closes_old_and_opens_new_history():
    """Test updating service price closes current active history and creates new one."""
    mock_db = MagicMock()
    service_id = uuid4()
    owner_id = uuid4()

    service = Service(
        id=service_id,
        name="Lunch Thali",
        price=80.0,
        currency="INR",
        unit="plate",
        is_active=True,
    )

    old_history = ServicePriceHistory(
        id=uuid4(),
        service_id=service_id,
        price=80.0,
        currency="INR",
        effective_from=datetime.now(timezone.utc) - timedelta(days=30),
        effective_to=None,
    )

    # First query retrieves the service; second query retrieves current_active price history
    mock_db.query.return_value.filter.return_value.first.return_value = service
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
        old_history
    )

    update_payload = ServiceUpdate(price=95.0, description="Updated hearty thali")

    updated = ServiceService.update_service(
        service_id=service_id,
        update_data=update_payload,
        db=mock_db,
        changed_by=owner_id,
    )

    assert updated is not None
    assert updated.price == 95.0
    assert updated.description == "Updated hearty thali"
    # Old history should now have effective_to set
    assert old_history.effective_to is not None
    # mock_db.add should be called for the new history entry
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_update_service_non_price_fields_no_new_history():
    """Test updating only non-price fields does not create a new price history entry."""
    mock_db = MagicMock()
    service_id = uuid4()

    service = Service(
        id=service_id,
        name="Old Name",
        price=80.0,
        currency="INR",
        unit="plate",
    )
    mock_db.query.return_value.filter.return_value.first.return_value = service

    update_payload = ServiceUpdate(name="New Name", unit="box")

    updated = ServiceService.update_service(
        service_id=service_id,
        update_data=update_payload,
        db=mock_db,
    )

    assert updated is not None
    assert updated.name == "New Name"
    assert updated.unit == "box"
    # No price change, so db.add should not be called
    mock_db.add.assert_not_called()
    mock_db.commit.assert_called_once()


def test_calculate_days_since_update():
    """Test days_since_update calculation for trust indicators."""
    now = datetime.now(timezone.utc)

    assert ServiceService.calculate_days_since_update(None) is None
    assert ServiceService.calculate_days_since_update(now) == 0

    five_days_ago = now - timedelta(days=5)
    assert ServiceService.calculate_days_since_update(five_days_ago) == 5

    thirty_days_ago = now - timedelta(days=30, hours=2)
    assert ServiceService.calculate_days_since_update(thirty_days_ago) == 30


def test_delete_service():
    """Test deleting a service calls db.delete."""
    mock_db = MagicMock()
    service_id = uuid4()
    service = Service(id=service_id, name="To Delete", price=50.0)
    mock_db.query.return_value.filter.return_value.first.return_value = service

    success = ServiceService.delete_service(service_id, mock_db)

    assert success is True
    mock_db.delete.assert_called_once_with(service)
    mock_db.commit.assert_called_once()
