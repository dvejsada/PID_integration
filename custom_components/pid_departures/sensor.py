"""Platform for sensor integration."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import timedelta, datetime
from typing import Any
from zoneinfo import ZoneInfo

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ICON_STOP, ICON_LAT, ICON_LON, ICON_ZONE, ICON_PLATFORM, ICON_UPDATE, ROUTE_TYPE_ICON, RouteType
from .entity import BaseEntity
from .hub import DepartureBoard

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Add sensors for passed config_entry in HA."""
    departure_board: DepartureBoard = hass.data[DOMAIN][config_entry.entry_id]  # type: ignore[Any]
    new_entities: list[Entity] = []

    # Set entities for departures
    for i in range(departure_board.conn_num):
        new_entities.append(RouteNameSensor(departure_board, i))
        new_entities.append(DepartureTimeSensor(departure_board, i))

    # Set diagnostic entities
    new_entities.append(StopSensor(departure_board))
    new_entities.append(LatSensor(departure_board))
    new_entities.append(LonSensor(departure_board))
    new_entities.append(ZoneSensor(departure_board))
    if departure_board.platform != "":
        new_entities.append(PlatformSensor(departure_board))
    new_entities.append(UpdateSensor(departure_board))

    # Add all entities to HA
    async_add_entities(new_entities)


class RouteNameSensor(BaseEntity, SensorEntity):
    """Sensor for departure route name."""

    _attr_translation_key = "route_name"
    _attr_should_poll = False

    def __init__(self, departure_board: DepartureBoard, departure_num: int) -> None:
        super().__init__(departure_board)
        self._departure = departure_num
        self._attr_unique_id = f"{departure_board.board_id}_{self.translation_key}_{departure_num + 1}"
        self._attr_translation_placeholders = {"num": str(departure_num + 1)}

    @property
    def native_value(self) -> str:
        """ Returns name of the route as state."""
        return self._departure_board.departures[self._departure].route_name or "?"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """ Returns dictionary of additional state attributes"""
        # NOTE: When CONF_LATITUDE and CONF_LONGITUDE is included, HASS shows
        #  the entity on the map.
        return {
            **self._departure_board.departures[self._departure].as_dict(),
            CONF_LATITUDE: self._departure_board.latitude,
            CONF_LONGITUDE: self._departure_board.longitude,
        }

    @property
    def icon(self) -> str:
        """Returns entity icon based on the type of route"""
        route_type = self._departure_board.departures[self._departure].route_type
        return ROUTE_TYPE_ICON.get(route_type, ROUTE_TYPE_ICON[RouteType.BUS])

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._departure_board.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._departure_board.remove_callback(self.async_write_ha_state)


class DepartureTimeSensor(BaseEntity, SensorEntity):
    """Sensor for the next departure time (estimated)."""

    _attr_translation_key = "departure_time"
    _attr_should_poll = False
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, departure_board: DepartureBoard, departure_num: int) -> None:
        super().__init__(departure_board)
        self._departure_num = departure_num
        self._attr_unique_id = f"{departure_board.board_id}_{self.translation_key}_{departure_num + 1}"
        self._attr_translation_placeholders = {"num": str(departure_num + 1)}

    @property
    def native_value(self) -> datetime | None:
        return self._departure_board.departures[self._departure_num].departure_time_est

    @property
    def icon(self) -> str:
        """Returns entity icon based on the type of route"""
        route_type = self._departure_board.departures[self._departure_num].route_type
        return ROUTE_TYPE_ICON.get(route_type, ROUTE_TYPE_ICON[RouteType.BUS])

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._departure_board.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._departure_board.remove_callback(self.async_write_ha_state)


class StopSensor(BaseEntity, SensorEntity):
    """Sensor for stop name."""

    _attr_translation_key = "stop_name"
    _attr_icon = ICON_STOP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    @property
    def native_value(self) -> str:
        return self._departure_board.stop_name


class LatSensor(BaseEntity, SensorEntity):
    """Sensor for latitude of the stop."""

    _attr_translation_key = "latitude"
    _attr_icon = ICON_LAT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    @property
    def native_value(self) -> float:
        return self._departure_board.latitude


class LonSensor(BaseEntity, SensorEntity):
    """Sensor for longitude of the stop."""

    _attr_translation_key = "longitude"
    _attr_icon = ICON_LON
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    @property
    def native_value(self) -> float:
        return self._departure_board.longitude


class ZoneSensor(BaseEntity, SensorEntity):
    """Sensor for zone."""

    _attr_translation_key = "zone"
    _attr_icon = ICON_ZONE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    @property
    def native_value(self) -> str:
        return self._departure_board.zone


class PlatformSensor(BaseEntity, SensorEntity):
    """Sensor for platform."""

    _attr_translation_key = "platform"
    _attr_icon = ICON_PLATFORM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    @property
    def native_value(self) -> str:
        return self._departure_board.platform


class UpdateSensor(BaseEntity, SensorEntity):
    """Sensor for API update."""

    _attr_translation_key = "updated"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = ICON_UPDATE
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, departure_board: DepartureBoard) -> None:
        super().__init__(departure_board)
        self._attr_native_value = datetime.now(tz=ZoneInfo("Europe/Prague"))

    async def async_update(self) -> None:
        """ Calls regular update of data from API. """
        await self._departure_board.async_update()
        self._attr_native_value = datetime.now(tz=ZoneInfo("Europe/Prague"))
