"""Prague Departure Board integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from .coordinator import PIDConfigEntry, PIDDepartureUpdateCoordinator

PLATFORMS: list[str] = ["sensor", "binary_sensor", "calendar"]


async def async_setup_entry(hass: HomeAssistant, entry: PIDConfigEntry) -> bool:
    """Set up Departure Board from a config entry."""
    coordinator = PIDDepartureUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PIDConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: PIDConfigEntry) -> None:
    """Reload the entry when its options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
