"""Prague Departure Board integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import hub
from .const import DOMAIN, CONF_DEP_NUM
from homeassistant.const import CONF_API_KEY, CONF_ID
from .dep_board_api import PIDDepartureBoardAPI

PLATFORMS: list[str] = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Departure Board from a config entry flow."""
    response = await hass.async_add_executor_job(PIDDepartureBoardAPI.update_info, entry.data[CONF_API_KEY], entry.data[CONF_ID], entry.data[CONF_DEP_NUM])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub.DepartureBoard(hass, entry.data[CONF_API_KEY], entry.data[CONF_ID], entry.data[CONF_DEP_NUM], response)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
