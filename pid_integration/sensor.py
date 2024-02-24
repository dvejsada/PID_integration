"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

from .const import ICON_BUS, ICON_TRAM, ICON_METRO, ICON_TRAIN, DOMAIN, ICON_STOP, ICON_LAT, ICON_LON, ICON_ZONE, ICON_PLATFORM, ICON_UPDATE
from homeassistant.const import EntityCategory


SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    departure_board = hass.data[DOMAIN][config_entry.entry_id]
    new_entities = []
    for i in range(departure_board.conn_num):
        new_entities.append(DepartureSensor(i, departure_board))
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
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def native_value(self):
        return self._departure_board.extra_attr[self._departure]["route"]["short_name"]

    @property
    def extra_state_attributes(self):
        return self._departure_board.extra_attr[self._departure]

    @property
    def name(self) -> str:
        """Return entity name"""
        return f"departure {self._departure+1}"

    @property
    def route_type(self):
        return self._departure_board.extra_attr[self._departure]["route"]["type"]

    @property
    def icon(self):
        """Return entity icon based on the type of vehicle"""
        if int(self.route_type) == 0:
            icon = ICON_TRAM
        elif int(self.route_type) == 1:
            icon = ICON_METRO
        elif int(self.route_type) == 2:
            icon = ICON_TRAIN
        else:
            icon = ICON_BUS
        return icon

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._departure_board.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._departure_board.remove_callback(self.async_write_ha_state)


class StopSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True
    _attr_icon = ICON_STOP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.stop_name

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def name(self) -> str:
        """Return entity name"""
        return "stop name"


class LatSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True
    _attr_icon = ICON_LAT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.latitude

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def name(self) -> str:
        """Return entity name"""
        return "latitude"


class LonSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True
    _attr_icon = ICON_LON
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.longitude

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def name(self) -> str:
        """Return entity name"""
        return "longitude"


class ZoneSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True
    _attr_icon = ICON_ZONE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.zone

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def name(self) -> str:
        """Return entity name"""
        return "zone"


class PlatformSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True
    _attr_icon = ICON_PLATFORM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = self._departure_board.platform

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def name(self) -> str:
        """Return entity name"""
        return "platform"


class UpdateSensor(SensorEntity):
    """Sensor for API update."""
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = ICON_UPDATE
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"
        self._attr_native_value = datetime.now(tz=ZoneInfo("Europe/Prague"))

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def name(self) -> str:
        """Return entity name"""
        return "updated"

    async def async_update(self):
        await self._departure_board.async_update()
        self._attr_native_value = datetime.now(tz=ZoneInfo("Europe/Prague"))

