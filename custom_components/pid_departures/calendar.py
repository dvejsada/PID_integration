"""Platform for calendar integration."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
import logging
from typing import Any, cast
from typing_extensions import override

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, STATE_ON
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt

from .const import CAL_EVENT_MIN_DURATION_SEC, CONF_CAL_EVENTS_NUM, DOMAIN, ICON_STOP, ROUTE_TYPE_ICON, RouteType
from .dep_board_api import PIDDepartureBoardAPI
from .entity import BaseEntity
from .hub import DepartureBoard, DepartureData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    departure_board: DepartureBoard = hass.data[DOMAIN][config_entry.entry_id]  # type: ignore[Any]
    events_count: int = config_entry.data[CONF_CAL_EVENTS_NUM]  # type: ignore[Any]
    async_add_entities([
        DeparturesCalendarEntity(departure_board, events_count=events_count),
    ])


class DeparturesCalendarEntity(BaseEntity, CalendarEntity):

    _attr_should_poll = False
    _attr_translation_key = "departures"

    def __init__(self, departure_board: DepartureBoard, events_count: int) -> None:
        super().__init__(departure_board)
        self._events_count = events_count
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
        return self._create_event(self._departure_board.departures[0])

    @property
    @override
    def icon(self) -> str:
        """Return entity icon based on the type of route."""
        if self.state == STATE_ON:
            route_type = self._departure_board.departures[0].route_type
            return ROUTE_TYPE_ICON.get(route_type, ROUTE_TYPE_ICON[RouteType.BUS])
        else:
            return ICON_STOP

    @property
    @override
    def extra_state_attributes(self) -> Mapping[str, Any]:
        # NOTE: When CONF_LATITUDE and CONF_LONGITUDE is included, HASS shows
        #  the entity on the map.
        return {
            **self._departure_board.departures[0].as_dict(),
            CONF_LATITUDE: self._departure_board.latitude,
            CONF_LONGITUDE: self._departure_board.longitude,
        }

    @override
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        if self._events_count == 0:
            return []
        time_before = dt.now() - start_date
        time_after = end_date - dt.now()

        if (not timedelta_in_range(time_before, *PIDDepartureBoardAPI.TIME_BEFORE_RANGE) and
            not timedelta_in_range(time_after, *PIDDepartureBoardAPI.TIME_AFTER_RANGE)):
            _LOGGER.debug(f"async_get_events: start_date={start_date} end_date={end_date} is out of range")
            return []

        data = await PIDDepartureBoardAPI.async_fetch_data(
            self._departure_board.api_key,
            self._departure_board.board_id,
            limit=self._events_count,
            time_before=timedelta_clamp(time_before, *PIDDepartureBoardAPI.TIME_BEFORE_RANGE),
            time_after=timedelta_clamp(time_after, *PIDDepartureBoardAPI.TIME_AFTER_RANGE))

        events = (
            self._create_event(DepartureData.from_api(dep))
            for dep in cast(list[dict[str, Any]], data["departures"])
        )
        return [event for event in events if event]

    def _create_event(self, departure: DepartureData) -> CalendarEvent | None:
        start = departure.arrival_time_est
        end = departure.departure_time_est

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

        route_type = self._translate(f"state_attributes.route_type.state.{departure.route_type}")
        short_name = departure.route_name or "?"

        return CalendarEvent(
            start=start,
            end=end,
            summary=f"{route_type} {short_name}",
            location=self._departure_board.name,
            description=f"Trip to {departure.trip_headsign}",
        )

    def _translate(self, key_path: str) -> str:
        # XXX: This is hack-ish, I haven't found the right approach for this.
        return self.platform.platform_translations[
            f"component.{self.platform.platform_name}.entity.{self.platform.domain}" +
            f".{self.translation_key}.{key_path}"]


def timedelta_clamp(delta: timedelta, min: timedelta, max: timedelta) -> timedelta:
    if delta < min:
        return min
    elif delta > max:
        return max
    else:
        return delta


def timedelta_in_range(delta: timedelta, min: timedelta, max: timedelta) -> bool:
    return min <= delta <= max
