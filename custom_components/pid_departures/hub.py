from __future__ import annotations

from attrs import asdict, converters, define, field, fields
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import reduce
from typing import Any, cast

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, RouteType
from .dep_board_api import PIDDepartureBoardAPI


# Based on PID Departure Board schema in https://api.golemio.cz/pid/docs/openapi/.
ROUTE_TYPES_NUM = {
    0: RouteType.TRAM,
    1: RouteType.METRO,
    2: RouteType.TRAIN,
    3: RouteType.BUS,
    4: RouteType.FERRY,
    7: RouteType.FUNICULAR,
    11: RouteType.TROLLEYBUS
}

def parse_route_type(num: int | None) -> RouteType:
    if num is None:
        return RouteType.UNKNOWN
    return ROUTE_TYPES_NUM.get(num) or RouteType.UNKNOWN

parse_datetime = converters.optional(datetime.fromisoformat)


# Based on PID Departure Board schema in https://api.golemio.cz/pid/docs/openapi/.
@define(kw_only=True)
class DepartureData:
    arrival_time_est: datetime | None = field(metadata={"src": "arrival_timestamp.predicted"}, converter=parse_datetime)
    arrival_time_sched: datetime | None = field(metadata={"src": "arrival_timestamp.scheduled"}, converter=parse_datetime)
    departure_time_est: datetime | None = field(metadata={"src": "departure_timestamp.predicted"}, converter=parse_datetime)
    departure_time_sched: datetime | None = field(metadata={"src": "departure_timestamp.scheduled"}, converter=parse_datetime)
    departure_in_min: str | None = field(metadata={"src": "departure_timestamp.minutes"})
    is_delay_avail: bool = field(metadata={"src": "delay.is_available"})
    delay_min: int | None = field(metadata={"src": "delay.minutes"})
    delay_sec: int | None = field(metadata={"src": "delay.seconds"})
    route_name: str | None = field(metadata={"src": "route.short_name"})
    route_type: RouteType = field(metadata={"src": "route.type"}, converter=parse_route_type)
    train_number: str | None = field(metadata={"src": "trip.short_name"})
    trip_id: str = field(metadata={"src": "trip.id"})
    trip_direction: str | None = field(metadata={"src": "trip.direction"})
    trip_headsign: str = field(metadata={"src": "trip.headsign"})
    is_air_conditioned: bool = field(metadata={"src": "trip.is_air_conditioned"})
    is_at_stop: bool = field(metadata={"src": "trip.is_at_stop"})
    is_canceled: bool = field(metadata={"src": "trip.is_canceled"})
    is_night: bool = field(metadata={"src": "route.is_night"})
    is_regional: bool = field(metadata={"src": "route.is_regional"})
    is_substitute: bool = field(metadata={"src": "route.is_substitute_transport"})
    is_wheelchair_accessible: bool = field(metadata={"src": "trip.is_wheelchair_accessible"})
    last_stop_id: str | None = field(metadata={"src": "last_stop.id"})
    last_stop_name: str | None = field(metadata={"src": "last_stop.name"})
    stop_id: str = field(metadata={"src": "stop.id"})
    stop_platform: str | None = field(metadata={"src": "stop.platform_code"})

    @staticmethod
    def from_api(data: dict[str, Any]) -> DepartureData:
        """Create a DepartureData from the PID Departure Board API response."""
        attrs: dict[str, Any] = {}
        for f in fields(DepartureData):  # type: ignore[Any]
            keypath: str = f.metadata["src"]  # type: ignore[Any]
            attrs[f.name] = dig(data, keypath.split("."))  # type: ignore[Any]
        return DepartureData(**attrs)  # type: ignore[Any]

    def as_dict(self) -> dict[str, Any]:
        """Return data as a dict."""
        return asdict(self)


class DepartureBoard:
    """Setting Departure board as device."""

    def __init__(self, hass: HomeAssistant, api_key: str, stop_id: str, conn_num: int, walking_offset: int = 0) -> None:
        """Initialize departure board."""
        super().__init__()
        self._hass = hass
        self._api_key: str = api_key
        self._stop_id: str = stop_id
        self.conn_num: int = int(conn_num)
        self.walking_offset: int = walking_offset  # User input in minutes (positive = future)
        self.response: dict[str, Any] = {}
        self._departures: list[DepartureData] = []
        self._callbacks: set[Callable[[], None]] = set()

    @property
    def board_id(self) -> str:
        """ID for departure board."""
        return self._stop_id

    @property
    def device_info(self) -> DeviceInfo:
        """ Provides a device info. """
        return {"identifiers": {(DOMAIN, self.board_id)}, "name": self.name, "manufacturer": "Prague Integrated Transport"}

    @property
    def name(self) -> str:
        """Provides name for departure board."""
        return self.stop_name + " " + self.platform

    @property
    def stop_name(self) -> str:
        """ Provides name of the stop."""
        return self.response["stops"][0]["stop_name"]  # type: ignore[Any]

    @property
    def platform(self) -> str:
        """ Provides platform of the stop."""
        if self.response["stops"][0]["platform_code"] is not None:
            value: str = self.response["stops"][0]["platform_code"]
        else:
            value = ""
        return value

    @property
    def departures(self) -> list[DepartureData]:
        """Return a list of fetched departures from this stop sorted from earliest to latest."""
        return self._departures

    @property
    def latitude(self) -> float:
        """ Returns latitude of the stop."""
        return self.response["stops"][0]["stop_lat"]  # type: ignore[Any]

    @property
    def longitude(self) -> float:
        """Returns longitude of the stop."""
        return self.response["stops"][0]["stop_lon"]  # type: ignore[Any]

    @property
    def api_key(self) -> str:
        """ Returns API key."""
        return self._api_key

    async def async_update(self) -> None:
        """ Updates the data from API."""
        # Convert user-friendly walking offset to API format
        # User: positive = future, negative = past (intuitive)
        # API: positive = past, negative = future (counter-intuitive)
        # So we invert the sign and convert minutes to timedelta
        api_offset_minutes = -self.walking_offset
        walking_offset_timedelta = timedelta(minutes=api_offset_minutes)

        data = await PIDDepartureBoardAPI.async_fetch_data(
            self.api_key,
            self._stop_id,
            self.conn_num,
            time_before=walking_offset_timedelta
        )
        self.response = data
        self._departures = [DepartureData.from_api(dep)
                            for dep in cast(list[dict[str, Any]], data["departures"])]
        await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when there are new data."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    async def publish_updates(self) -> None:
        """Schedule call to all registered callbacks."""
        for callback in self._callbacks:
            callback()

    @property
    def wheelchair_accessible(self) -> int:
        """Returns wheelchair accessibility of the stop."""
        return int(self.response["stops"][0]["wheelchair_boarding"])  # type: ignore[Any]

    @property
    def zone(self) -> str:
        """Zone of the stop"""
        return self.response["stops"][0]["zone_id"]  # type: ignore[Any]

    @property
    def info_text(self) -> tuple[bool, dict[str, Any]]:
        """ State and content of info text"""
        if len(self.response["infotexts"]) != 0:  # type: ignore[Any]
            state = True
            text: dict[str, Any] = self.response["infotexts"][0]
        else:
            state = False
            text = {}

        return state, text


def dig(d: dict[str, Any], keypath: list[str]) -> Any:  # type: ignore[Any]
    return reduce(dict.__getitem__, keypath, d)  # type: ignore[reportUnknownArgumentType]
