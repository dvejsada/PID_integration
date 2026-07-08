"""Data update coordinator for the PID Departure Board integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any, cast

from attrs import define
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import CONF_CAL_EVENTS_NUM, CONF_DEP_NUM, CONF_WALKING_OFFSET, DOMAIN, SCAN_INTERVAL
from .dep_board_api import PIDDepartureBoardAPI
from .errors import CannotConnect, StopNotFound, WrongApiKey
from .hub import DepartureData

_LOGGER = logging.getLogger(__name__)

PIDConfigEntry = ConfigEntry["PIDDepartureUpdateCoordinator"]


@define
class BoardData:
    """Parsed state of a single departure board."""

    departures: list[DepartureData]
    stop_name: str
    platform: str
    latitude: float
    longitude: float
    zone: str
    wheelchair_boarding: int
    infotexts: list[dict[str, Any]]

    @staticmethod
    def from_response(response: dict[str, Any]) -> "BoardData":
        """Create a BoardData from the PID Departure Board API response."""
        stop = response["stops"][0]
        return BoardData(
            departures=[
                DepartureData.from_api(dep)
                for dep in cast(list[dict[str, Any]], response["departures"])
            ],
            stop_name=stop["stop_name"],
            platform=stop["platform_code"] or "",
            latitude=stop["stop_lat"],
            longitude=stop["stop_lon"],
            zone=stop["zone_id"],
            wheelchair_boarding=int(stop["wheelchair_boarding"]),
            infotexts=response.get("infotexts", []),
        )


class PIDDepartureUpdateCoordinator(DataUpdateCoordinator[BoardData]):
    """Coordinator polling the Golemio departure board API for a single stop."""

    config_entry: PIDConfigEntry

    def __init__(self, hass: HomeAssistant, entry: PIDConfigEntry) -> None:
        """Initialize the coordinator from a config entry."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self._session = async_get_clientsession(hass)
        self.api_key: str = entry.data[CONF_API_KEY]
        self.stop_id: str = entry.data[CONF_ID]
        # Tunables live in options with a fallback to data for legacy entries.
        self.conn_num: int = int(self._option(CONF_DEP_NUM, 1))
        self.walking_offset: int = int(self._option(CONF_WALKING_OFFSET, 0))
        self.cal_events_count: int = int(self._option(CONF_CAL_EVENTS_NUM, 0))
        self.last_updated: datetime | None = None

    def _option(self, key: str, default: Any) -> Any:
        """Read a tunable from options, falling back to data, then default."""
        entry = self.config_entry
        return entry.options.get(key, entry.data.get(key, default))

    @property
    def _walking_offset_timedelta(self) -> timedelta:
        """Convert the user-friendly walking offset to the API's time_before.

        User: positive = future, negative = past (intuitive).
        API: positive = past, negative = future (counter-intuitive).
        So the sign is inverted.
        """
        return timedelta(minutes=-self.walking_offset)

    async def _async_update_data(self) -> BoardData:
        """Fetch the latest departure board data from the API."""
        try:
            data = await PIDDepartureBoardAPI.async_fetch_data(
                self._session,
                self.api_key,
                self.stop_id,
                self.conn_num,
                time_before=self._walking_offset_timedelta,
            )
        except WrongApiKey as err:
            raise ConfigEntryAuthFailed("Invalid API key") from err
        except StopNotFound as err:
            raise UpdateFailed(f"Stop {self.stop_id} was not found by the API") from err
        except CannotConnect as err:
            raise UpdateFailed("Error communicating with the API") from err

        self.last_updated = dt_util.now()
        return BoardData.from_response(data)

    async def async_get_departures(
        self, limit: int, time_before: timedelta, time_after: timedelta
    ) -> list[DepartureData]:
        """Fetch a custom range of departures (used by the calendar platform)."""
        data = await PIDDepartureBoardAPI.async_fetch_data(
            self._session,
            self.api_key,
            self.stop_id,
            limit,
            time_before=time_before,
            time_after=time_after,
        )
        return [
            DepartureData.from_api(dep)
            for dep in cast(list[dict[str, Any]], data["departures"])
        ]

    # Convenience accessors used by the entities. -------------------------

    @property
    def board_id(self) -> str:
        """Stable ID for the departure board (the stop ASW ID)."""
        return self.stop_id

    @property
    def name(self) -> str:
        """Display name for the departure board."""
        return (self.data.stop_name + " " + self.data.platform).strip()

    @property
    def device_info(self) -> DeviceInfo:
        """Provide device info for the departure board."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.board_id)},
            name=self.name,
            manufacturer="Prague Integrated Transport",
        )

    @property
    def departures(self) -> list[DepartureData]:
        """Return the fetched departures, earliest first."""
        return self.data.departures

    @property
    def stop_name(self) -> str:
        """Name of the stop."""
        return self.data.stop_name

    @property
    def platform(self) -> str:
        """Platform code of the stop."""
        return self.data.platform

    @property
    def latitude(self) -> float:
        """Latitude of the stop."""
        return self.data.latitude

    @property
    def longitude(self) -> float:
        """Longitude of the stop."""
        return self.data.longitude

    @property
    def zone(self) -> str:
        """Fare zone of the stop."""
        return self.data.zone

    @property
    def wheelchair_accessible(self) -> int:
        """Wheelchair accessibility of the stop."""
        return self.data.wheelchair_boarding

    @property
    def info_text(self) -> tuple[bool, dict[str, Any]]:
        """State and content of the first info text."""
        if self.data.infotexts:
            return True, self.data.infotexts[0]
        return False, {}
