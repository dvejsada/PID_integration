"""Serves the bundled Lovelace card and registers it with the frontend."""
from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

CARD_FILENAME = "pid-departures-card.js"
CARD_URL = f"/{DOMAIN}/{CARD_FILENAME}"
CARD_PATH = Path(__file__).parent / "www" / CARD_FILENAME


async def async_register_card(hass: HomeAssistant) -> None:
    """Serve the card and load it on every dashboard, no Lovelace resource needed."""
    try:
        # Home Assistant 2024.7+
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths([StaticPathConfig(CARD_URL, str(CARD_PATH), True)])
    except ImportError:
        hass.http.register_static_path(CARD_URL, str(CARD_PATH), True)

    # The file is served with long cache headers, the version busts the browser cache on upgrade.
    integration = await async_get_integration(hass, DOMAIN)
    add_extra_js_url(hass, f"{CARD_URL}?v={integration.version}")
