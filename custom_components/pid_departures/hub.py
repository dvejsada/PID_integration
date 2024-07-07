from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .dep_board_api import PIDDepartureBoardAPI


class DepartureBoard:
    """Setting Departure board as device."""

    def __init__(self, hass: HomeAssistant, api_key: str, stop_id: str, conn_num: int, response: dict[str, Any]) -> None:
        """Initialize departure board."""
        super().__init__()
        self._hass = hass
        self._api_key: str = api_key
        self._stop_id: str = stop_id
        self.conn_num: int = int(conn_num)
        self.response: dict[str, Any] = response
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
    def extra_attr(self) -> list[dict[str, Any]]:
        """ Returns extra state attributes (departures)."""
        return self.response["departures"]  # type: ignore[Any]

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
        data = await PIDDepartureBoardAPI.async_fetch_data(self.api_key, self._stop_id, self.conn_num)
        self.response = data
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
