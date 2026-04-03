"""Persistent storage for Supply Manager."""

import logging
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)


class SupplyStorage:
    """Handle persistent storage for supplies and logs."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage."""
        self._hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.supplies: dict[str, dict[str, Any]] = {}
        self.consumption_log: list[dict[str, Any]] = []
        self.storage_log: list[dict[str, Any]] = []

    async def async_load(self) -> None:
        """Load data from storage."""
        data = await self._store.async_load()
        if data:
            self.supplies = data.get("supplies", {})
            self.consumption_log = data.get("consumption_log", [])
            self.storage_log = data.get("storage_log", [])
        _LOGGER.debug("Loaded %d supplies from storage", len(self.supplies))

    async def _async_save(self) -> None:
        """Save data to storage."""
        await self._store.async_save(
            {
                "supplies": self.supplies,
                "consumption_log": self.consumption_log,
                "storage_log": self.storage_log,
            }
        )

    def generate_supply_id(self) -> str:
        """Generate a unique supply ID."""
        import uuid

        return str(uuid.uuid4())[:8]

    async def async_add_supply(self, supply_data: dict[str, Any]) -> str:
        """Add a new supply to storage."""
        supply_id = self.generate_supply_id()
        now = datetime.now().isoformat()

        supply = {
            "supply_id": supply_id,
            "name": supply_data["name"],
            "category": supply_data.get("category", "other"),
            "quantity": supply_data["quantity"],
            "unit": supply_data.get("unit", "pcs"),
            "min_threshold": supply_data.get("min_threshold", 0),
            "expiration_date": supply_data.get("expiration_date"),
            "location": supply_data.get("location", ""),
            "notes": supply_data.get("notes", ""),
            "created_at": now,
            "updated_at": now,
        }

        self.supplies[supply_id] = supply

        log_entry = {
            "timestamp": now,
            "action": "added",
            "supply_id": supply_id,
            "supply_name": supply["name"],
            "quantity": supply["quantity"],
            "unit": supply["unit"],
            "user": supply_data.get("user", "system"),
            "details": f"Added {supply['quantity']} {supply['unit']} of {supply['name']}",
        }
        self.storage_log.append(log_entry)

        await self._async_save()
        _LOGGER.info("Added supply: %s (ID: %s)", supply["name"], supply_id)
        return supply_id

    async def async_update_supply(
        self, supply_id: str, updates: dict[str, Any], user: str = "system"
    ) -> bool:
        """Update an existing supply."""
        if supply_id not in self.supplies:
            _LOGGER.warning("Supply %s not found for update", supply_id)
            return False

        supply = self.supplies[supply_id]
        old_quantity = supply["quantity"]
        now = datetime.now().isoformat()

        for key, value in updates.items():
            if key in supply and key not in ("supply_id", "created_at"):
                supply[key] = value

        supply["updated_at"] = now

        log_entry = {
            "timestamp": now,
            "action": "updated",
            "supply_id": supply_id,
            "supply_name": supply["name"],
            "old_quantity": old_quantity,
            "new_quantity": supply["quantity"],
            "unit": supply["unit"],
            "user": user,
            "details": f"Updated {supply['name']}: {old_quantity} -> {supply['quantity']} {supply['unit']}",
        }
        self.storage_log.append(log_entry)

        await self._async_save()
        _LOGGER.info("Updated supply: %s (ID: %s)", supply["name"], supply_id)
        return True

    async def async_remove_supply(self, supply_id: str, user: str = "system") -> bool:
        """Remove a supply from storage."""
        if supply_id not in self.supplies:
            _LOGGER.warning("Supply %s not found for removal", supply_id)
            return False

        supply = self.supplies.pop(supply_id)
        now = datetime.now().isoformat()

        log_entry = {
            "timestamp": now,
            "action": "removed",
            "supply_id": supply_id,
            "supply_name": supply["name"],
            "quantity": supply["quantity"],
            "unit": supply["unit"],
            "user": user,
            "details": f"Removed {supply['name']} ({supply['quantity']} {supply['unit']})",
        }
        self.storage_log.append(log_entry)

        await self._async_save()
        _LOGGER.info("Removed supply: %s (ID: %s)", supply["name"], supply_id)
        return True

    async def async_log_consumption(
        self,
        supply_id: str,
        quantity: float,
        user: str = "system",
        reason: str = "",
    ) -> bool:
        """Log consumption of a supply."""
        if supply_id not in self.supplies:
            _LOGGER.warning("Supply %s not found for consumption logging", supply_id)
            return False

        supply = self.supplies[supply_id]
        now = datetime.now().isoformat()

        new_quantity = max(0, supply["quantity"] - quantity)
        supply["quantity"] = new_quantity
        supply["updated_at"] = now

        consumption_entry = {
            "timestamp": now,
            "supply_id": supply_id,
            "supply_name": supply["name"],
            "category": supply["category"],
            "quantity_consumed": quantity,
            "unit": supply["unit"],
            "remaining_quantity": new_quantity,
            "user": user,
            "reason": reason,
        }
        self.consumption_log.append(consumption_entry)

        storage_log_entry = {
            "timestamp": now,
            "action": "consumed",
            "supply_id": supply_id,
            "supply_name": supply["name"],
            "quantity_consumed": quantity,
            "remaining_quantity": new_quantity,
            "unit": supply["unit"],
            "user": user,
            "reason": reason,
            "details": f"Consumed {quantity} {supply['unit']} of {supply['name']} by {user}",
        }
        self.storage_log.append(storage_log_entry)

        await self._async_save()
        _LOGGER.info(
            "Logged consumption: %s - %s %s by %s",
            supply["name"],
            quantity,
            supply["unit"],
            user,
        )

        if new_quantity <= supply["min_threshold"]:
            return "low_stock"

        return True

    def get_supply(self, supply_id: str) -> dict[str, Any] | None:
        """Get a single supply by ID."""
        return self.supplies.get(supply_id)

    def get_all_supplies(self) -> list[dict[str, Any]]:
        """Get all supplies."""
        return list(self.supplies.values())

    def get_supplies_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get supplies filtered by category."""
        return [s for s in self.supplies.values() if s["category"] == category]

    def get_low_stock_supplies(self) -> list[dict[str, Any]]:
        """Get supplies that are at or below their minimum threshold."""
        return [
            s for s in self.supplies.values() if s["quantity"] <= s["min_threshold"]
        ]

    def get_consumption_log(
        self,
        supply_id: str | None = None,
        user: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get consumption log with optional filters."""
        results = self.consumption_log

        if supply_id:
            results = [e for e in results if e["supply_id"] == supply_id]
        if user:
            results = [e for e in results if e["user"] == user]
        if start_date:
            results = [e for e in results if e["timestamp"] >= start_date]
        if end_date:
            results = [e for e in results if e["timestamp"] <= end_date]

        return results[-limit:]

    def get_storage_log(
        self,
        supply_id: str | None = None,
        action: str | None = None,
        user: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get storage operation log with optional filters."""
        results = self.storage_log

        if supply_id:
            results = [e for e in results if e.get("supply_id") == supply_id]
        if action:
            results = [e for e in results if e.get("action") == action]
        if user:
            results = [e for e in results if e.get("user") == user]

        return results[-limit:]

    def get_total_supplies(self) -> int:
        """Get total number of supplies."""
        return len(self.supplies)

    def get_total_stock_value(self) -> dict[str, int]:
        """Get total stock count by category."""
        counts: dict[str, int] = {}
        for supply in self.supplies.values():
            cat = supply["category"]
            counts[cat] = counts.get(cat, 0) + 1
        return counts
