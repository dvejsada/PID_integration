from __future__ import annotations

from homeassistant.core import HomeAssistant
from .api_call import ApiCall


def check_not_null(response):
    if response is not None:
        value = response
    else:
        value = ""
    return value


class DepartureBoard:
    """setting Departure board device"""

    def __init__(self, hass: HomeAssistant, api_key: str, stop_id: str, conn_num: int, response) -> None:
        """Init departure board."""
        self._hass = hass
        self._api_key = api_key
        self._stop_id = stop_id
        self._id = stop_id
        self.conn_num = conn_num
        self.departures = []
        self._stop_name = response["stops"][0]["stop_name"]
        self._name = response["stops"][0]["stop_name"] + " " + check_not_null(response["stops"][0]["platform_code"])
        self._wheel = response["stops"][0]["wheelchair_boarding"]
        self.latitude = response["stops"][0]["stop_lat"]
        self.longitude = response["stops"][0]["stop_lon"]
        self.platform = check_not_null(response["stops"][0]["platform_code"])
        self.zone = response["stops"][0]["zone_id"]
        self.extra_attr = response["departures"]
        for i in range(self.conn_num):
            self.departures.append(i)

    @property
    def board_id(self) -> str:
        """ID for departure board."""
        return self._id

    @property
    def name(self) -> str:
        """ID for departure board."""
        return self._name

    @property
    def stop_name(self) -> str:
        """Stop name."""
        return self._stop_name

    async def async_update(self) -> None:
        data = await self._hass.async_add_executor_job(ApiCall.update_info, self._api_key, self._stop_id, self.conn_num)
        self.extra_attr = data["departures"]

    @property
    def wheelchair_accessible(self):
        return self._wheel

