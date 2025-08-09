"""
Defining constants for the project.
"""
from aiohttp import ClientTimeout
from enum import StrEnum, auto
from typing import Final


class RouteType(StrEnum):
    UNKNOWN = auto()
    TRAM = auto()
    METRO = auto()
    TRAIN = auto()
    BUS = auto()
    FERRY = auto()
    FUNICULAR = auto()
    TROLLEYBUS = auto()


API_URL = "https://api.golemio.cz/v2/pid/departureboards"
HTTP_TIMEOUT: Final = ClientTimeout(total=10)

ICON_STOP = "mdi:bus-stop-uncovered"
ICON_WHEEL = "mdi:wheelchair"
ICON_LAT = "mdi:latitude"
ICON_LON = "mdi:longitude"
ICON_PLATFORM = "mdi:bus-stop-covered"
ICON_ZONE = "mdi:map-clock"
ICON_INFO_ON = "mdi:alert-outline"
ICON_INFO_OFF = "mdi:check-circle-outline"
ICON_UPDATE = "mdi:update"
DOMAIN = "pid_departures"
CONF_CAL_EVENTS_NUM = "cal_events_number"
CONF_DEP_NUM = "departures_number"
CONF_STOP_SEL = "stop_selector"
CONF_WALKING_OFFSET = "walking_offset"

ROUTE_TYPE_ICON: Final = {
    RouteType.TRAM: "mdi:tram",
    RouteType.METRO: "mdi:train-variant",
    RouteType.TRAIN: "mdi:train",
    RouteType.BUS: "mdi:bus",
    RouteType.FERRY: "mdi:ferry",
    RouteType.FUNICULAR: "mdi:gondola",
    RouteType.TROLLEYBUS: "mdi:bus-electric",
}

CAL_EVENT_MIN_DURATION_SEC = 15
