"""Frontend registration for Supply Manager."""

import logging
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PANEL_URL = "/api/supply_manager/panel.js"
PANEL_PATH = "www/panel.js"

CARDS = [
    {"url": "/api/supply_manager/card.js", "path": "www/supply-card.js"},
    {"url": "/api/supply_manager/overview_card.js", "path": "www/overview-card.js"},
    {"url": "/api/supply_manager/log_card.js", "path": "www/log-card.js"},
]


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Register the custom panel and cards."""
    www_path = Path(__file__).parent / "www"

    if not www_path.exists():
        _LOGGER.warning("www directory not found at %s", www_path)
        return

    static_paths = []

    for card in CARDS:
        card_path = www_path / card["path"]
        if card_path.exists():
            static_paths.append(StaticPathConfig(card["url"], str(card_path), False))
            _LOGGER.debug("Registered card at %s", card["url"])

    panel_path = www_path / PANEL_PATH
    if panel_path.exists():
        static_paths.append(StaticPathConfig(PANEL_URL, str(panel_path), False))

        try:
            from homeassistant.components.frontend import async_register_panel

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
        except ImportError:
            _LOGGER.warning("Frontend panel not available in this HA version")
        except Exception as err:
            _LOGGER.warning("Failed to register panel: %s", err)

    if static_paths:
        await hass.http.async_register_static_paths(static_paths)
        _LOGGER.info("Registered %d static paths", len(static_paths))


async def async_unregister_frontend(hass: HomeAssistant) -> None:
    """Unregister the custom panel."""
    try:
        from homeassistant.components.frontend import async_remove_panel

        async_remove_panel(hass, "supply-manager-panel")
        _LOGGER.info("Unregistered Supply Manager panel")
    except ImportError:
        pass
    except Exception as err:
        _LOGGER.debug("Error unregistering panel: %s", err)
