"""Platform for sensor integration."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import timedelta, datetime
from typing import Any
from zoneinfo import ZoneInfo

from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ICON_STOP, ICON_LAT, ICON_LON, ICON_ZONE, ICON_PLATFORM, ICON_UPDATE, ROUTE_TYPE_ICON
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
        new_entities.append(DepartureSensor(i, departure_board))

    # Set diagnostic entities
    new_entities.append(StopSensor(departure_board.conn_num+1, departure_board))
    new_entities.append(LatSensor(departure_board.conn_num+2, departure_board))
    new_entities.append(LonSensor(departure_board.conn_num+3, departure_board))
    new_entities.append(ZoneSensor(departure_board.conn_num+4, departure_board))
    if departure_board.platform != "":
        new_entities.append(PlatformSensor(departure_board.conn_num+5, departure_board))
    new_entities.append(UpdateSensor(departure_board.conn_num+6, departure_board))

    # Add all entities to HA
    async_add_entities(new_entities)


class DepartureSensor(SensorEntity):
    """Sensor for departure."""
    _attr_translation_key = "departure"
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board: DepartureBoard) -> None:
        super().__init__()
        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_translation_placeholders = {"num": str(departure + 1)}

    @property
    def device_info(self) -> DeviceInfo:
        """Return information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def native_value(self) -> str:
        """ Returns name of the route as state."""
        return self._departure_board.extra_attr[self._departure]["route"]["short_name"]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """ Returns dictionary of additional state attributes"""
        return self._departure_board.extra_attr[self._departure]

    @property
    def route_type(self) -> str:
        """ Returns the type of the route (bus/tram/metro). """
        return self._departure_board.extra_attr[self._departure]["route"]["type"]

    @property
    def icon(self) -> str:
        """Returns entity icon based on the type of route"""
        return ROUTE_TYPE_ICON.get(int(self.route_type), ROUTE_TYPE_ICON[3])

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._departure_board.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._departure_board.remove_callback(self.async_write_ha_state)


class StopSensor(SensorEntity):
    """Sensor for stop name."""
    _attr_translation_key = "stop_name"
    _attr_has_entity_name = True
    _attr_icon = ICON_STOP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board: DepartureBoard) -> None:
        super().__init__()
        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.stop_name

    @property
    def device_info(self) -> DeviceInfo:
        """Returns information to link this entity with the correct device."""
        return self._departure_board.device_info


class LatSensor(SensorEntity):
    """Sensor for latitude of the stop."""
    _attr_translation_key = "latitude"
    _attr_has_entity_name = True
    _attr_icon = ICON_LAT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board: DepartureBoard) -> None:
        super().__init__()
        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.latitude

    @property
    def device_info(self) -> DeviceInfo:
        """Returns information to link this entity with the correct device."""
        return self._departure_board.device_info


class LonSensor(SensorEntity):
    """Sensor for longitude of the stop."""
    _attr_translation_key = "longitude"
    _attr_has_entity_name = True
    _attr_icon = ICON_LON
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board: DepartureBoard) -> None:
        super().__init__()
        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.longitude

    @property
    def device_info(self) -> DeviceInfo:
        """Returns information to link this entity with the correct device."""
        return self._departure_board.device_info


class ZoneSensor(SensorEntity):
    """Sensor for zone."""
    _attr_translation_key = "zone"
    _attr_has_entity_name = True
    _attr_icon = ICON_ZONE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board: DepartureBoard) -> None:
        super().__init__()
        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.zone

    @property
    def device_info(self) -> DeviceInfo:
        """Returns information to link this entity with the correct device."""
        return self._departure_board.device_info


class PlatformSensor(SensorEntity):
    """Sensor for platform."""
    _attr_translation_key = "platform"
    _attr_has_entity_name = True
    _attr_icon = ICON_PLATFORM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board: DepartureBoard) -> None:
        super().__init__()
        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.platform

    @property
    def device_info(self) -> DeviceInfo:
        """Returns information to link this entity with the correct device."""
        return self._departure_board.device_info


class UpdateSensor(SensorEntity):
    """Sensor for API update."""
    _attr_translation_key = "updated"
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = ICON_UPDATE
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, departure: int, departure_board: DepartureBoard) -> None:
        super().__init__()
        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = datetime.now(tz=ZoneInfo("Europe/Prague"))

    @property
    def device_info(self) -> DeviceInfo:
        """Returns information to link this entity with the correct device."""
        return self._departure_board.device_info

    async def async_update(self):
        """ Calls regular update of data from API. """
        await self._departure_board.async_update()
        self._attr_native_value = datetime.now(tz=ZoneInfo("Europe/Prague"))
