"""Services for Supply Manager."""

import logging
from datetime import datetime

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_CATEGORY,
    ATTR_END_DATE,
    ATTR_EXPIRATION_DATE,
    ATTR_LOCATION,
    ATTR_MIN_THRESHOLD,
    ATTR_NAME,
    ATTR_NOTES,
    ATTR_QUANTITY,
    ATTR_REASON,
    ATTR_START_DATE,
    ATTR_SUPPLY_ID,
    ATTR_UNIT,
    ATTR_USER,
    DOMAIN,
    EVENT_CONSUMPTION_LOGGED,
    EVENT_LOW_STOCK_ALERT,
    EVENT_SUPPLY_ADDED,
    EVENT_SUPPLY_REMOVED,
    EVENT_SUPPLY_UPDATED,
    SERVICE_ADD_SUPPLY,
    SERVICE_GET_CONSUMPTION_LOG,
    SERVICE_GET_LOW_STOCK,
    SERVICE_GET_SUPPLY_HISTORY,
    SERVICE_LOG_CONSUMPTION,
    SERVICE_REMOVE_SUPPLY,
    SERVICE_UPDATE_STOCK,
    SUPPLY_CATEGORIES,
    UNITS,
)

_LOGGER = logging.getLogger(__name__)

ADD_SUPPLY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_NAME): cv.string,
        vol.Required(ATTR_QUANTITY): vol.Coerce(float),
        vol.Optional(ATTR_CATEGORY, default="other"): vol.In(SUPPLY_CATEGORIES),
        vol.Optional(ATTR_UNIT, default="pcs"): vol.In(UNITS),
        vol.Optional(ATTR_MIN_THRESHOLD, default=0): vol.Coerce(float),
        vol.Optional(ATTR_EXPIRATION_DATE): cv.string,
        vol.Optional(ATTR_LOCATION, default=""): cv.string,
        vol.Optional(ATTR_NOTES, default=""): cv.string,
        vol.Optional(ATTR_USER, default="system"): cv.string,
    }
)

UPDATE_STOCK_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SUPPLY_ID): cv.string,
        vol.Required(ATTR_QUANTITY): vol.Coerce(float),
        vol.Optional(ATTR_USER, default="system"): cv.string,
    }
)

LOG_CONSUMPTION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SUPPLY_ID): cv.string,
        vol.Required(ATTR_QUANTITY): vol.Coerce(float),
        vol.Optional(ATTR_USER, default="system"): cv.string,
        vol.Optional(ATTR_REASON, default=""): cv.string,
    }
)

REMOVE_SUPPLY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SUPPLY_ID): cv.string,
        vol.Optional(ATTR_USER, default="system"): cv.string,
    }
)

GET_LOW_STOCK_SCHEMA = vol.Schema({})

GET_SUPPLY_HISTORY_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_SUPPLY_ID): cv.string,
        vol.Optional(ATTR_START_DATE): cv.string,
        vol.Optional(ATTR_END_DATE): cv.string,
        vol.Optional("limit", default=100): vol.Coerce(int),
    }
)

GET_CONSUMPTION_LOG_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_SUPPLY_ID): cv.string,
        vol.Optional(ATTR_USER): cv.string,
        vol.Optional(ATTR_START_DATE): cv.string,
        vol.Optional(ATTR_END_DATE): cv.string,
        vol.Optional("limit", default=100): vol.Coerce(int),
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Supply Manager."""

    async def handle_add_supply(call: ServiceCall) -> None:
        """Handle add supply service."""
        coordinator = _get_coordinator(hass)
        supply_data = {
            "name": call.data[ATTR_NAME],
            "category": call.data[ATTR_CATEGORY],
            "quantity": call.data[ATTR_QUANTITY],
            "unit": call.data[ATTR_UNIT],
            "min_threshold": call.data[ATTR_MIN_THRESHOLD],
            "expiration_date": call.data.get(ATTR_EXPIRATION_DATE),
            "location": call.data[ATTR_LOCATION],
            "notes": call.data[ATTR_NOTES],
            "user": call.data[ATTR_USER],
        }

        supply_id = await coordinator.async_add_supply(supply_data)
        supply = coordinator.storage.get_supply(supply_id)

        hass.bus.async_fire(
            EVENT_SUPPLY_ADDED,
            {
                "supply_id": supply_id,
                "name": supply["name"],
                "quantity": supply["quantity"],
                "unit": supply["unit"],
                "category": supply["category"],
            },
        )

        _LOGGER.info("Service add_supply: Added %s", supply["name"])

    async def handle_update_stock(call: ServiceCall) -> None:
        """Handle update stock service."""
        coordinator = _get_coordinator(hass)
        supply_id = call.data[ATTR_SUPPLY_ID]
        quantity = call.data[ATTR_QUANTITY]
        user = call.data[ATTR_USER]

        result = await coordinator.async_update_supply(
            supply_id, {"quantity": quantity}, user
        )

        if result:
            supply = coordinator.storage.get_supply(supply_id)
            hass.bus.async_fire(
                EVENT_SUPPLY_UPDATED,
                {
                    "supply_id": supply_id,
                    "name": supply["name"],
                    "old_quantity": call.data.get("old_quantity"),
                    "new_quantity": quantity,
                    "unit": supply["unit"],
                    "user": user,
                },
            )

        _LOGGER.info("Service update_stock: Updated %s", supply_id)

    async def handle_log_consumption(call: ServiceCall) -> None:
        """Handle log consumption service."""
        coordinator = _get_coordinator(hass)
        supply_id = call.data[ATTR_SUPPLY_ID]
        quantity = call.data[ATTR_QUANTITY]
        user = call.data[ATTR_USER]
        reason = call.data[ATTR_REASON]

        result = await coordinator.async_log_consumption(
            supply_id, quantity, user, reason
        )

        supply = coordinator.storage.get_supply(supply_id)
        hass.bus.async_fire(
            EVENT_CONSUMPTION_LOGGED,
            {
                "supply_id": supply_id,
                "name": supply["name"],
                "quantity_consumed": quantity,
                "remaining": supply["quantity"],
                "unit": supply["unit"],
                "user": user,
                "reason": reason,
            },
        )

        if result == "low_stock":
            hass.bus.async_fire(
                EVENT_LOW_STOCK_ALERT,
                {
                    "supply_id": supply_id,
                    "name": supply["name"],
                    "remaining": supply["quantity"],
                    "min_threshold": supply["min_threshold"],
                    "unit": supply["unit"],
                },
            )

        _LOGGER.info(
            "Service log_consumption: %s consumed %s %s",
            user,
            quantity,
            supply["name"],
        )

    async def handle_remove_supply(call: ServiceCall) -> None:
        """Handle remove supply service."""
        coordinator = _get_coordinator(hass)
        supply_id = call.data[ATTR_SUPPLY_ID]
        user = call.data[ATTR_USER]

        supply = coordinator.storage.get_supply(supply_id)
        if supply:
            supply_name = supply["name"]
        else:
            supply_name = "unknown"

        result = await coordinator.async_remove_supply(supply_id, user)

        if result:
            hass.bus.async_fire(
                EVENT_SUPPLY_REMOVED,
                {
                    "supply_id": supply_id,
                    "name": supply_name,
                    "user": user,
                },
            )

        _LOGGER.info("Service remove_supply: Removed %s", supply_id)

    async def handle_get_low_stock(call: ServiceCall) -> None:
        """Handle get low stock service."""
        coordinator = _get_coordinator(hass)
        low_stock = coordinator.storage.get_low_stock_supplies()

        hass.bus.async_fire(
            "supply_manager_low_stock_result",
            {
                "count": len(low_stock),
                "items": low_stock,
            },
        )

        _LOGGER.info("Service get_low_stock: Found %d low stock items", len(low_stock))

    async def handle_get_supply_history(call: ServiceCall) -> None:
        """Handle get supply history service."""
        coordinator = _get_coordinator(hass)
        supply_id = call.data.get(ATTR_SUPPLY_ID)
        start_date = call.data.get(ATTR_START_DATE)
        end_date = call.data.get(ATTR_END_DATE)
        limit = call.data["limit"]

        history = coordinator.storage.get_storage_log(
            supply_id=supply_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        hass.bus.async_fire(
            "supply_manager_history_result",
            {
                "count": len(history),
                "log": history,
            },
        )

    async def handle_get_consumption_log(call: ServiceCall) -> None:
        """Handle get consumption log service."""
        coordinator = _get_coordinator(hass)
        supply_id = call.data.get(ATTR_SUPPLY_ID)
        user = call.data.get(ATTR_USER)
        start_date = call.data.get(ATTR_START_DATE)
        end_date = call.data.get(ATTR_END_DATE)
        limit = call.data["limit"]

        log = coordinator.storage.get_consumption_log(
            supply_id=supply_id,
            user=user,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        hass.bus.async_fire(
            "supply_manager_consumption_result",
            {
                "count": len(log),
                "log": log,
            },
        )

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_SUPPLY, handle_add_supply, schema=ADD_SUPPLY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_STOCK, handle_update_stock, schema=UPDATE_STOCK_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LOG_CONSUMPTION,
        handle_log_consumption,
        schema=LOG_CONSUMPTION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_SUPPLY,
        handle_remove_supply,
        schema=REMOVE_SUPPLY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_LOW_STOCK,
        handle_get_low_stock,
        schema=GET_LOW_STOCK_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_SUPPLY_HISTORY,
        handle_get_supply_history,
        schema=GET_SUPPLY_HISTORY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_CONSUMPTION_LOG,
        handle_get_consumption_log,
        schema=GET_CONSUMPTION_LOG_SCHEMA,
    )


def _get_coordinator(hass: HomeAssistant):
    """Get the first available coordinator."""
    domain_data = hass.data.get(DOMAIN, {})
    for entry_id, data in domain_data.items():
        return data["coordinator"]
    raise ValueError("No Supply Manager config entry found")


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Supply Manager services."""
    hass.services.async_remove(DOMAIN, SERVICE_ADD_SUPPLY)
    hass.services.async_remove(DOMAIN, SERVICE_UPDATE_STOCK)
    hass.services.async_remove(DOMAIN, SERVICE_LOG_CONSUMPTION)
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_SUPPLY)
    hass.services.async_remove(DOMAIN, SERVICE_GET_LOW_STOCK)
    hass.services.async_remove(DOMAIN, SERVICE_GET_SUPPLY_HISTORY)
    hass.services.async_remove(DOMAIN, SERVICE_GET_CONSUMPTION_LOG)
