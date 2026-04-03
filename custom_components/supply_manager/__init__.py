"""Supply Manager integration for Home Assistant."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import SupplyCoordinator
from .services import async_setup_services, async_unload_services
from .storage import SupplyStorage

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Supply Manager component from yaml config."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Supply Manager from a config entry."""
    storage = SupplyStorage(hass)
    await storage.async_load()

    coordinator = SupplyCoordinator(hass, storage)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "storage": storage,
    }

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "supply_manager_hub")},
        name="Supply Manager",
        manufacturer="Custom",
        model="Supply Manager Hub",
        sw_version="1.0.0",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass)

    try:
        from .frontend import async_register_frontend

        await async_register_frontend(hass)
    except Exception as err:
        _LOGGER.warning("Failed to register frontend: %s", err)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        await async_unload_services(hass)
        try:
            from .frontend import async_unregister_frontend

            await async_unregister_frontend(hass)
        except Exception:
            pass

    return unload_ok
