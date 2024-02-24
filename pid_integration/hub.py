from __future__ import annotations

from homeassistant.core import HomeAssistant
from .api_call import ApiCall
from collections.abc import Callable
from .const import DOMAIN


class DepartureBoard:
    """setting Departure board as device"""

    def __init__(self, hass: HomeAssistant, api_key: str, stop_id: str, conn_num: int, response) -> None:
        """Init departure board."""
        self._hass = hass
        self._api_key = api_key
        self._stop_id = stop_id
        self.conn_num = int(conn_num)
        self.response = response
        self._callbacks = set()

    @property
    def board_id(self) -> str:
        """ID for departure board."""
        return self._stop_id

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.board_id)}, "name": self.name, "manufacturer": "Prague Integrated Transport"}

    @property
    def name(self) -> str:
        """ID for departure board."""
        return self.stop_name + " " + self.platform

    @property
    def stop_name(self) -> str:
        """Stop name."""
        return self.response["stops"][0]["stop_name"]

    @property
    def platform(self) -> str:
        """Platform."""
        if self.response["stops"][0]["platform_code"] is not None:
            value = self.response["stops"][0]["platform_code"]
        else:
            value = ""
        return value

    @property
    def extra_attr(self) -> str:
        """Extra state attributes (departures)."""
        return self.response["departures"]

    @property
    def latitude(self) -> str:
        """Latitude of the stop."""
        return self.response["stops"][0]["stop_lat"]

    @property
    def longitude(self) -> str:
        """Longitude of the stop."""
        return self.response["stops"][0]["stop_lon"]

    @property
    def api_key(self) -> str:
        """Provides API key."""
        return self._api_key

    async def async_update(self) -> None:
        data = await self._hass.async_add_executor_job(ApiCall.update_info, self.api_key, self._stop_id, self.conn_num)
        self.response = data
        await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when there are new data."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

    @property
    def wheelchair_accessible(self):
        """Wheelchair accessibility of the stop."""
        return int(self.response["stops"][0]["wheelchair_boarding"])

    @property
    def zone(self) -> str:
        """Zone of the stop"""
        return self.response["stops"][0]["zone_id"]

    @property
    def info_text(self) -> tuple:
        """ State and content of info text"""
        if len(self.response["infotexts"]) != 0:
            state = True
            text = self.response["infotexts"][0]
        else:
            state = False
            text = {}

        return state, text
