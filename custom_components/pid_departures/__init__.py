"""Prague Departure Board integration."""
from __future__ import annotations

from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .coordinator import PIDConfigEntry, PIDDepartureUpdateCoordinator

PLATFORMS: list[str] = ["sensor", "binary_sensor", "calendar"]


async def async_setup_entry(hass: HomeAssistant, entry: PIDConfigEntry) -> bool:
    """Set up Departure Board from a config entry."""
    _async_set_missing_unique_id(hass, entry)

    coordinator = PIDDepartureUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    _async_remove_surplus_departure_entities(hass, entry, coordinator.conn_num)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PIDConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _async_set_missing_unique_id(hass: HomeAssistant, entry: PIDConfigEntry) -> None:
    """Give entries created before unique IDs were introduced the stop ID as unique ID.

    Without it, adding the same stop again would not be detected as a duplicate.
    """
    if entry.unique_id is not None:
        return
    stop_id: str = entry.data[CONF_ID]
    if any(
        other.unique_id == stop_id
        for other in hass.config_entries.async_entries(DOMAIN)
        if other.entry_id != entry.entry_id
    ):
        # The stop was already added twice before; keep the duplicate as it is.
        return
    hass.config_entries.async_update_entry(entry, unique_id=stop_id)


def _async_remove_surplus_departure_entities(
    hass: HomeAssistant, entry: PIDConfigEntry, departures_number: int
) -> None:
    """Remove departure entities left over after the number of departures was lowered."""
    registry = er.async_get(hass)
    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        # Unique IDs of departure entities: {stop_id}_{route_name|departure_time}_{n}
        prefix, _, num = entity.unique_id.rpartition("_")
        if (
            num.isdigit()
            and int(num) > departures_number
            and prefix.endswith(("_route_name", "_departure_time"))
        ):
            registry.async_remove(entity.entity_id)


async def _async_update_listener(hass: HomeAssistant, entry: PIDConfigEntry) -> None:
    """Reload the entry when its options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
