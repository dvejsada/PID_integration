import logging
import requests
from typing import Any

from .const import API_URL
from .errors import CannotConnect, StopNotFound, WrongApiKey

_LOGGER = logging.getLogger(__name__)


class PIDDepartureBoardAPI:

    @staticmethod
    def fetch_data(api_key: str, stop_id: str, conn_num: int) -> dict[str, Any]:
        """Get new data from API."""
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {"aswIds": stop_id, "total": conn_num, "minutesAfter": 4320}
        response = requests.get(API_URL, params=parameters, headers=headers)
        status = response.status_code

        if status == 200:
            data: dict[str, Any] = response.json()
            return data
        elif status == 401:
            raise WrongApiKey
        elif status == 404:
            raise StopNotFound
        else:
            _LOGGER.error(f"GET {response.url} returned HTTP {status}")
            raise CannotConnect
