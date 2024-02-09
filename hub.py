from __future__ import annotations

from homeassistant.core import HomeAssistant
from .api_call import ApiCall
import asyncio


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
        self._name = response["stops"][0]["stop_name"]
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

    async def async_update(self) -> None:
        data = await self._hass.async_add_executor_job(ApiCall.update_info, self._api_key, self._stop_id, self.conn_num)
        self.extra_attr = data["departures"]

