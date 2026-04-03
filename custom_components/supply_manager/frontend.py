"""Frontend registration for Supply Manager."""

import logging
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.components.frontend import async_register_panel
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PANEL_URL = "/supply_manager_panel.js"
PANEL_PATH = "www/panel.js"

CARDS = [
    {
        "url": "/supply_manager_card.js",
        "path": "www/supply-card.js",
        "name": "supply-card",
    },
    {
        "url": "/supply_manager_overview_card.js",
        "path": "www/overview-card.js",
        "name": "supply-overview-card",
    },
    {
        "url": "/supply_manager_log_card.js",
        "path": "www/log-card.js",
        "name": "supply-log-card",
    },
]


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register the custom panel and cards."""
    www_path = Path(__file__).parent / "www"

    if not www_path.exists():
        _LOGGER.warning("www directory not found at %s", www_path)
        return

    for card in CARDS:
        card_path = www_path / card["path"]
        if card_path.exists():
            await hass.http.async_register_static_paths(
                [StaticPathConfig(card["url"], str(card_path), False)]
            )
            _LOGGER.debug("Registered card: %s at %s", card["name"], card["url"])

    panel_path = www_path / PANEL_PATH
    if panel_path.exists():
        await hass.http.async_register_static_paths(
            [StaticPathConfig(PANEL_URL, str(panel_path), False)]
        )

        async_register_panel(
            hass,
            "supply-manager-panel",
            "Supply Manager",
            PANEL_URL,
            sidebar_title="Supply Manager",
            sidebar_icon="mdi:package-variant",
            require_admin=False,
            config={},
        )
        _LOGGER.info("Registered Supply Manager panel")
    else:
        _LOGGER.warning("Panel file not found at %s", panel_path)


async def async_unregister_frontend(hass: HomeAssistant) -> None:
    """Unregister the custom panel."""
    try:
        from homeassistant.components.frontend import async_remove_panel

        async_remove_panel(hass, "supply-manager-panel")
        _LOGGER.info("Unregistered Supply Manager panel")
    except Exception as err:
        _LOGGER.debug("Error unregistering panel: %s", err)
