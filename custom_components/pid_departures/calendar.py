"""Platform for calendar integration."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
import logging
from typing import Any
from typing_extensions import override

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt

from custom_components.pid_departures.dep_board_api import PIDDepartureBoardAPI

from .const import DOMAIN, CAL_EVENT_MIN_DURATION_SEC, CAL_EVENTS_COUNT_LIMIT
from .hub import DepartureBoard

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    departure_board: DepartureBoard = hass.data[DOMAIN][config_entry.entry_id]  # type: ignore[Any]
    async_add_entities([DeparturesCalendarEntity(departure_board)])


class DeparturesCalendarEntity(CalendarEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_translation_key = "departures"

    def __init__(self, departure_board: DepartureBoard) -> None:
        super().__init__()
        self._attr_unique_id = f"{departure_board.board_id}_{departure_board.conn_num}"
        self._attr_translation_placeholders = {
            "stop_name": departure_board.name,
        }
        self._departure_board = departure_board
        self._event: CalendarEvent | None = None

    @override
    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._departure_board.register_callback(self.async_write_ha_state)

    @override
    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._departure_board.remove_callback(self.async_write_ha_state)

    @property
    @override
    def event(self) -> CalendarEvent | None:
        """Return the current or next upcoming event."""
        return self._create_event(self._departure_board.extra_attr[0])

    @property
    @override
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return self._departure_board.extra_attr[0]

    @override
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        time_before = dt.now() - start_date
        time_after = end_date - dt.now()

        if (not timedelta_in_range(time_before, *PIDDepartureBoardAPI.TIME_BEFORE_RANGE) and
            not timedelta_in_range(time_after, *PIDDepartureBoardAPI.TIME_AFTER_RANGE)):
            _LOGGER.debug(f"async_get_events: start_date={start_date} end_date={end_date} is out of range")
            return []

        data = await PIDDepartureBoardAPI.async_fetch_data(
            self._departure_board.api_key,
            self._departure_board.board_id,
            limit=CAL_EVENTS_COUNT_LIMIT,
            time_before=timedelta_clamp(time_before, *PIDDepartureBoardAPI.TIME_BEFORE_RANGE),
            time_after=timedelta_clamp(time_after, *PIDDepartureBoardAPI.TIME_AFTER_RANGE))

        events = (self._create_event(dep) for dep in data["departures"])
        return [event for event in events if event]

    def _create_event(self, departure: dict[str, Any]) -> CalendarEvent | None:
        start = try_parse_timestamp(departure["arrival_timestamp"]["predicted"])  # type: ignore[Any]
        end = try_parse_timestamp(departure["departure_timestamp"]["predicted"])  # type: ignore[Any]

        if not start and not end:
            _LOGGER.error('Invalid data, both "arrival_timestamp" and "departure_timestamp" is null')
            return None
        elif start:
            # departure_timestamp is null on last stops.
            if not end or (end - start).seconds < CAL_EVENT_MIN_DURATION_SEC:
                end = start + timedelta(seconds=CAL_EVENT_MIN_DURATION_SEC)
        elif end:
            # arrival_timestamp is null on first stops.
            start = end - timedelta(seconds=CAL_EVENT_MIN_DURATION_SEC)

        route_type_code: int = departure["route"]["type"]
        route_type_name = self._translate(f"state_attributes.route_type.state.{route_type_code}")
        short_name: str = departure["route"]["short_name"]

        return CalendarEvent(
            start=start,
            end=end,
            summary=f"{route_type_name} {short_name}",
            location=self._departure_board.name,
        )

    def _translate(self, key_path: str) -> str | None:
        # XXX: This is hack-ish, I haven't found the right approach for this.
        return self.platform.platform_translations.get(
            f"component.{self.platform.platform_name}.entity.{self.platform.domain}" +
            f".{self.translation_key}.{key_path}")


def try_parse_timestamp(input: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat(input or "")
    except ValueError:
        return None


def timedelta_clamp(delta: timedelta, min: timedelta, max: timedelta) -> timedelta:
    if delta < min:
        return min
    elif delta > max:
        return max
    else:
        return delta


def timedelta_in_range(delta: timedelta, min: timedelta, max: timedelta) -> bool:
    return min <= delta <= max
