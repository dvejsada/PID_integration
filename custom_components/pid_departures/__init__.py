"""Prague Departure Board integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_DEP_NUM, CONF_WALKING_OFFSET
from .errors import CannotConnect, StopNotFound, WrongApiKey
from .frontend import async_register_card
from .hub import DepartureBoard

PLATFORMS: list[str] = ["sensor", "binary_sensor", "calendar"]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration, runs once regardless of the number of departure boards."""
    await async_register_card(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Departure Board from a config entry flow."""
    walking_offset = entry.data.get(CONF_WALKING_OFFSET, 0)
    hub = DepartureBoard(
        hass,
        entry.data[CONF_API_KEY],
        entry.data[CONF_ID],
        entry.data[CONF_DEP_NUM],
        walking_offset
    )  # type: ignore[Any]
    try:
        await hub.async_update()
    except CannotConnect:
        # try again later again
        raise ConfigEntryNotReady from None
    except StopNotFound:
        return False
    except WrongApiKey:
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub  # type: ignore[Any]

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)  # type: ignore[Any]

    return unload_ok
