"""
Defining constants for the project.
"""
from aiohttp import ClientTimeout
from typing import Final

API_URL = "https://api.golemio.cz/v2/pid/departureboards/"
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

ROUTE_TYPE_ICON: Final = {
    0: "mdi:tram",
    1: "mdi:train-variant",
    2: "mdi:train",
    3: "mdi:bus",
    4: "mdi:ferry",
    7: "mdi:gondola",
    11: "mdi:bus-electric",
}

CAL_EVENT_MIN_DURATION_SEC = 15
