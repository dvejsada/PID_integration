from __future__ import annotations

from attrs import asdict, converters, define, field, fields
from datetime import datetime
from functools import reduce
from typing import Any

from .const import RouteType


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


def dig(d: dict[str, Any], keypath: list[str]) -> Any:  # type: ignore[Any]
    return reduce(dict.__getitem__, keypath, d)  # type: ignore[reportUnknownArgumentType]
