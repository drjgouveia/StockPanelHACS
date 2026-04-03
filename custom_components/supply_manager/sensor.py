"""Sensor platform for Supply Manager."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SupplyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up supply sensors from a config entry."""
    coordinator: SupplyCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        SupplyTotalSensor(coordinator),
        SupplyLowStockSensor(coordinator),
    ]

    for supply in coordinator.storage.get_all_supplies():
        entities.append(SupplyStockSensor(coordinator, supply["supply_id"]))

    async_add_entities(entities)


class SupplyTotalSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total number of supplies."""

    _attr_name = "Total Supplies"
    _attr_unique_id = "supply_manager_total"
    _attr_icon = "mdi:package-variant"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: SupplyCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "supply_manager_hub")},
            name="Supply Manager",
        )

    @property
    def native_value(self) -> int:
        """Return the total number of supplies."""
        return self.coordinator.data.get("total_supplies", 0)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return {
            "stock_by_category": self.coordinator.data.get("stock_by_category", {}),
        }


class SupplyLowStockSensor(CoordinatorEntity, SensorEntity):
    """Sensor for low stock alerts."""

    _attr_name = "Low Stock Alerts"
    _attr_unique_id = "supply_manager_low_stock"
    _attr_icon = "mdi:alert-circle"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: SupplyCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "supply_manager_hub")},
            name="Supply Manager",
        )

    @property
    def native_value(self) -> int:
        """Return the number of low stock items."""
        return len(self.coordinator.data.get("low_stock", []))

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        low_stock = self.coordinator.data.get("low_stock", [])
        return {
            "low_stock_items": [
                {
                    "name": s["name"],
                    "quantity": s["quantity"],
                    "min_threshold": s["min_threshold"],
                    "unit": s["unit"],
                    "category": s["category"],
                }
                for s in low_stock
            ],
        }


class SupplyStockSensor(CoordinatorEntity, SensorEntity):
    """Sensor for individual supply stock level."""

    def __init__(self, coordinator: SupplyCoordinator, supply_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._supply_id = supply_id
        supply = coordinator.storage.get_supply(supply_id)
        self._attr_name = f"{supply['name']} Stock"
        self._attr_unique_id = f"supply_manager_{supply_id}"
        self._attr_icon = self._get_icon(supply["category"])
        self._attr_native_unit_of_measurement = supply["unit"]
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "supply_manager_hub")},
            name="Supply Manager",
        )

    def _get_icon(self, category: str) -> str:
        """Get icon based on category."""
        icons = {
            "medicine": "mdi:pill",
            "food": "mdi:food-apple",
            "water": "mdi:water",
            "cleaning": "mdi:broom",
            "hygiene": "mdi:soap",
            "other": "mdi:package-variant",
        }
        return icons.get(category, "mdi:package-variant")

    @property
    def native_value(self) -> float:
        """Return the current stock quantity."""
        supply = self.coordinator.storage.get_supply(self._supply_id)
        if supply:
            return supply["quantity"]
        return 0

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        supply = self.coordinator.storage.get_supply(self._supply_id)
        if not supply:
            return {}

        return {
            "supply_id": supply["supply_id"],
            "category": supply["category"],
            "min_threshold": supply["min_threshold"],
            "expiration_date": supply.get("expiration_date"),
            "location": supply.get("location", ""),
            "notes": supply.get("notes", ""),
            "created_at": supply.get("created_at"),
            "updated_at": supply.get("updated_at"),
            "is_low_stock": supply["quantity"] <= supply["min_threshold"],
        }
