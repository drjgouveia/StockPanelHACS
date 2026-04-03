"""Coordinator for Supply Manager."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .storage import SupplyStorage

_LOGGER = logging.getLogger(__name__)


class SupplyCoordinator(DataUpdateCoordinator):
    """Coordinator to manage supplies data."""

    def __init__(self, hass: HomeAssistant, storage: SupplyStorage) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self.storage = storage

    async def _async_update_data(self) -> dict:
        """Fetch data from storage."""
        return {
            "supplies": self.storage.get_all_supplies(),
            "total_supplies": self.storage.get_total_supplies(),
            "low_stock": self.storage.get_low_stock_supplies(),
            "stock_by_category": self.storage.get_total_stock_value(),
        }

    async def async_add_supply(self, supply_data: dict) -> str:
        """Add a new supply and refresh."""
        supply_id = await self.storage.async_add_supply(supply_data)
        await self.async_request_refresh()
        return supply_id

    async def async_update_supply(
        self, supply_id: str, updates: dict, user: str = "system"
    ) -> bool:
        """Update a supply and refresh."""
        result = await self.storage.async_update_supply(supply_id, updates, user)
        if result:
            await self.async_request_refresh()
        return result

    async def async_remove_supply(self, supply_id: str, user: str = "system") -> bool:
        """Remove a supply and refresh."""
        result = await self.storage.async_remove_supply(supply_id, user)
        if result:
            await self.async_request_refresh()
        return result

    async def async_log_consumption(
        self, supply_id: str, quantity: float, user: str = "system", reason: str = ""
    ) -> bool | str:
        """Log consumption and refresh."""
        result = await self.storage.async_log_consumption(
            supply_id, quantity, user, reason
        )
        await self.async_request_refresh()
        return result
