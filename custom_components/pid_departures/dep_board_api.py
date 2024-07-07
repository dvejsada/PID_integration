from datetime import timedelta
import logging
from typing import Any
from urllib.parse import urlencode

import aiohttp

from .const import API_URL, HTTP_TIMEOUT
from .errors import CannotConnect, StopNotFound, WrongApiKey

_LOGGER = logging.getLogger(__name__)


class PIDDepartureBoardAPI:
    # According to docs https://api.golemio.cz/pid/docs/openapi.
    TIME_BEFORE_RANGE = (timedelta(minutes=-4320), timedelta(minutes=30))
    TIME_AFTER_RANGE = (timedelta(minutes=-4320), timedelta(minutes=4320))
    DEFAULT_TIME_BEFORE = timedelta(0)
    DEFAULT_TIME_AFTER = timedelta(minutes=4320)

    @staticmethod
    async def async_fetch_data(
        api_key: str,
        stop_id: str,
        limit: int = 1,
        time_before: timedelta = DEFAULT_TIME_BEFORE,
        time_after: timedelta = DEFAULT_TIME_AFTER,
    ) -> dict[str, Any]:
        """Get new data from API."""
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {
            "aswIds": stop_id,
            "limit": limit,
            "minutesBefore": int(time_before.total_seconds() / 60),
            "minutesAfter": int(time_after.total_seconds() / 60),
        }

        _LOGGER.debug(f"GET {API_URL}?{urlencode(parameters)}")
        async with (
            aiohttp.ClientSession(raise_for_status=False, timeout=HTTP_TIMEOUT) as http,
            http.get(API_URL, params=parameters, headers=headers) as resp
        ):
            if _LOGGER.isEnabledFor(logging.DEBUG):
                body = await resp.text()
                _LOGGER.debug(f"Received response for GET {API_URL}: HTTP {resp.status}\n" +
                              ellipsis(body, 1024))
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


def ellipsis(text: str, maxlen: int) -> str:
    if len(text) > maxlen:
        return text[:(maxlen - 3)] + "..."
    else:
        return text
