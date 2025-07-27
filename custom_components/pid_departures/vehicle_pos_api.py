from datetime import timedelta
import logging
from typing import Any
from urllib.parse import urlencode

import aiohttp

from .const import VEHICLEPOS_API_URL, HTTP_TIMEOUT
from .errors import CannotConnect, TripNotFound, WrongApiKey

_LOGGER = logging.getLogger(__name__)


class PIDVehiclePositionsAPI:
    @staticmethod
    async def async_fetch_data(
        api_key: str,
        gtfs_trip_id: str,
    ) -> dict[str, Any]:
        """Get new data from Vehicle Positions API."""
        headers = {"Content-Type": "application/json; charset=utf-8", "x-access-token": api_key}
        parameters = {
            "includeNotTracking": "false",  # Don't enrich dataset
            "includePositions": "false",  # Only get trip info, not positions.
        }

        _LOGGER.debug(f"GET {VEHICLEPOS_API_URL}/{gtfs_trip_id}?{urlencode(parameters)}")
        async with (
            aiohttp.ClientSession(raise_for_status=False, timeout=HTTP_TIMEOUT) as http,
            http.get(f"{VEHICLEPOS_API_URL}/{gtfs_trip_id}", params=parameters, headers=headers) as resp
        ):
            if _LOGGER.isEnabledFor(logging.DEBUG):
                body = await resp.text()
                _LOGGER.debug(f"Received response for GET {VEHICLEPOS_API_URL}: HTTP {resp.status}\n" +
                              ellipsis(body, 1024))
            if resp.status == 200:
                data: dict[str, Any] = await resp.json()
                return data
            elif resp.status == 401:
                raise WrongApiKey
            elif resp.status == 404:
                _LOGGER.error(f"Trip with ID {gtfs_trip_id} not found: {await resp.text()}")
                raise TripNotFound
            else:
                _LOGGER.error(f"GET {resp.url} returned HTTP {resp.status}")
                raise CannotConnect
