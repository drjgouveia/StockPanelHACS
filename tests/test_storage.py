"""Tests for Supply Manager storage."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from custom_components.supply_manager.storage import SupplyStorage


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    return hass


@pytest.fixture
def mock_store():
    """Create a mock Store."""
    store = AsyncMock()
    store.async_load = AsyncMock(return_value=None)
    store.async_save = AsyncMock()
    return store


@pytest.fixture
async def storage(mock_hass, mock_store):
    """Create a SupplyStorage instance with mocked dependencies."""
    with patch(
        "custom_components.supply_manager.storage.Store", return_value=mock_store
    ):
        s = SupplyStorage(mock_hass)
        s._store = mock_store
        await s.async_load()
        return s


@pytest.mark.asyncio
async def test_add_supply(storage):
    """Test adding a new supply."""
    supply_data = {
        "name": "Ibuprofen",
        "category": "medicine",
        "quantity": 50,
        "unit": "tablets",
        "min_threshold": 10,
        "user": "test_user",
    }

    supply_id = await storage.async_add_supply(supply_data)

    assert supply_id is not None
    assert supply_id in storage.supplies
    assert storage.supplies[supply_id]["name"] == "Ibuprofen"
    assert storage.supplies[supply_id]["quantity"] == 50
    assert len(storage.storage_log) == 1
    assert storage.storage_log[0]["action"] == "added"


@pytest.mark.asyncio
async def test_update_supply(storage):
    """Test updating an existing supply."""
    supply_data = {
        "name": "Rice",
        "category": "food",
        "quantity": 5,
        "unit": "kg",
        "user": "test_user",
    }
    supply_id = await storage.async_add_supply(supply_data)

    result = await storage.async_update_supply(
        supply_id, {"quantity": 10}, user="test_user"
    )

    assert result is True
    assert storage.supplies[supply_id]["quantity"] == 10
    assert len(storage.storage_log) == 2
    assert storage.storage_log[1]["action"] == "updated"


@pytest.mark.asyncio
async def test_remove_supply(storage):
    """Test removing a supply."""
    supply_data = {
        "name": "Water",
        "category": "water",
        "quantity": 20,
        "unit": "L",
        "user": "test_user",
    }
    supply_id = await storage.async_add_supply(supply_data)

    result = await storage.async_remove_supply(supply_id, user="test_user")

    assert result is True
    assert supply_id not in storage.supplies
    assert len(storage.storage_log) == 2
    assert storage.storage_log[1]["action"] == "removed"


@pytest.mark.asyncio
async def test_log_consumption(storage):
    """Test logging consumption of a supply."""
    supply_data = {
        "name": "Aspirin",
        "category": "medicine",
        "quantity": 30,
        "unit": "tablets",
        "min_threshold": 5,
        "user": "test_user",
    }
    supply_id = await storage.async_add_supply(supply_data)

    result = await storage.async_log_consumption(
        supply_id, 5, user="john", reason="Headache"
    )

    assert result is True
    assert storage.supplies[supply_id]["quantity"] == 25
    assert len(storage.consumption_log) == 1
    assert storage.consumption_log[0]["quantity_consumed"] == 5
    assert storage.consumption_log[0]["user"] == "john"
    assert len(storage.storage_log) == 2


@pytest.mark.asyncio
async def test_log_consumption_low_stock(storage):
    """Test consumption triggering low stock alert."""
    supply_data = {
        "name": "Bandages",
        "category": "medicine",
        "quantity": 10,
        "unit": "pcs",
        "min_threshold": 5,
        "user": "test_user",
    }
    supply_id = await storage.async_add_supply(supply_data)

    result = await storage.async_log_consumption(
        supply_id, 8, user="jane", reason="First aid"
    )

    assert result == "low_stock"
    assert storage.supplies[supply_id]["quantity"] == 2


@pytest.mark.asyncio
async def test_get_low_stock_supplies(storage):
    """Test getting low stock supplies."""
    await storage.async_add_supply(
        {
            "name": "Low Item",
            "category": "food",
            "quantity": 2,
            "unit": "pcs",
            "min_threshold": 5,
        }
    )
    await storage.async_add_supply(
        {
            "name": "OK Item",
            "category": "food",
            "quantity": 20,
            "unit": "pcs",
            "min_threshold": 5,
        }
    )

    low_stock = storage.get_low_stock_supplies()

    assert len(low_stock) == 1
    assert low_stock[0]["name"] == "Low Item"


@pytest.mark.asyncio
async def test_get_consumption_log(storage):
    """Test retrieving consumption log."""
    supply_data = {
        "name": "Test Supply",
        "category": "other",
        "quantity": 100,
        "unit": "pcs",
    }
    supply_id = await storage.async_add_supply(supply_data)

    await storage.async_log_consumption(supply_id, 10, user="alice")
    await storage.async_log_consumption(supply_id, 5, user="bob")

    log = storage.get_consumption_log()
    assert len(log) == 2

    log_by_user = storage.get_consumption_log(user="alice")
    assert len(log_by_user) == 1
    assert log_by_user[0]["user"] == "alice"


@pytest.mark.asyncio
async def test_get_supplies_by_category(storage):
    """Test filtering supplies by category."""
    await storage.async_add_supply(
        {
            "name": "Medicine A",
            "category": "medicine",
            "quantity": 10,
            "unit": "pcs",
        }
    )
    await storage.async_add_supply(
        {
            "name": "Food B",
            "category": "food",
            "quantity": 20,
            "unit": "kg",
        }
    )
    await storage.async_add_supply(
        {
            "name": "Medicine C",
            "category": "medicine",
            "quantity": 15,
            "unit": "tablets",
        }
    )

    medicines = storage.get_supplies_by_category("medicine")
    assert len(medicines) == 2

    foods = storage.get_supplies_by_category("food")
    assert len(foods) == 1


@pytest.mark.asyncio
async def test_get_storage_log(storage):
    """Test retrieving storage operation log."""
    supply_data = {
        "name": "Log Test",
        "category": "other",
        "quantity": 50,
        "unit": "pcs",
    }
    supply_id = await storage.async_add_supply(supply_data)
    await storage.async_update_supply(supply_id, {"quantity": 60}, user="admin")
    await storage.async_remove_supply(supply_id, user="admin")

    all_log = storage.get_storage_log()
    assert len(all_log) == 3

    add_log = storage.get_storage_log(action="added")
    assert len(add_log) == 1

    admin_log = storage.get_storage_log(user="admin")
    assert len(admin_log) == 2


@pytest.mark.asyncio
async def test_get_total_stock_value(storage):
    """Test getting total stock value by category."""
    await storage.async_add_supply(
        {
            "name": "Item 1",
            "category": "medicine",
            "quantity": 10,
            "unit": "pcs",
        }
    )
    await storage.async_add_supply(
        {
            "name": "Item 2",
            "category": "medicine",
            "quantity": 20,
            "unit": "pcs",
        }
    )
    await storage.async_add_supply(
        {
            "name": "Item 3",
            "category": "food",
            "quantity": 5,
            "unit": "kg",
        }
    )

    counts = storage.get_total_stock_value()
    assert counts["medicine"] == 2
    assert counts["food"] == 1
