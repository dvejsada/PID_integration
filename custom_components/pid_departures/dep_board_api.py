import aiohttp
import logging
from typing import Any
from urllib.parse import urlencode

from .const import API_URL, HTTP_TIMEOUT
from .errors import CannotConnect, StopNotFound, WrongApiKey

_LOGGER = logging.getLogger(__name__)


class PIDDepartureBoardAPI:

    @staticmethod
    async def async_fetch_data(api_key: str, stop_id: str, conn_num: int) -> dict[str, Any]:
        """Get new data from API."""
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {"aswIds": stop_id, "total": conn_num, "minutesAfter": 4320}

        _LOGGER.debug(f"GET {API_URL}?{urlencode(parameters)}")
        async with (
            aiohttp.ClientSession(raise_for_status=False, timeout=HTTP_TIMEOUT) as http,
            http.get(API_URL, params=parameters, headers=headers) as resp
        ):
            if resp.status == 200:
                data: dict[str, Any] = await resp.json()
                return data
            elif resp.status == 401:
                raise WrongApiKey
            elif resp.status == 404:
                raise StopNotFound
            else:
                _LOGGER.error(f"GET {resp.url} returned HTTP {resp.status}")
                raise CannotConnect
