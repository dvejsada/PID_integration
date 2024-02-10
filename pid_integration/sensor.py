"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (SensorEntity)

from datetime import timedelta

from .const import ICON_BUS, ICON_TRAM, ICON_METRO, ICON_TRAIN, DOMAIN, ICON_STOP, ICON_WHEEL, ICON_LAT, ICON_LON, ICON_ZONE, ICON_PLATFORM
from homeassistant.const import EntityCategory


SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    departure_board = hass.data[DOMAIN][config_entry.entry_id]
    new_entities = []
    for i in departure_board.departures:
        new_entities.append(DepartureSensor(departure_board.departures[i], departure_board))
    new_entities.append(StopSensor(int(departure_board.conn_num)+1, departure_board))
    new_entities.append(WheelchairSensor(int(departure_board.conn_num)+2, departure_board))
    new_entities.append(LatSensor(int(departure_board.conn_num)+3, departure_board))
    new_entities.append(LonSensor(int(departure_board.conn_num)+4, departure_board))
    new_entities.append(ZoneSensor(int(departure_board.conn_num)+5, departure_board))
    new_entities.append(PlatformSensor(int(departure_board.conn_num)+6, departure_board))
    # Add all entities to HA

    async_add_entities(new_entities)


class DepartureSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

        # The name of the entity
        self._attr_name = f"departure {self._departure+1}"
        self._state = self._departure_board.extra_attr[self._departure]["route"]["short_name"]
        self._extra_attr = self._departure_board.extra_attr[self._departure]
        self._route_type = self._departure_board.extra_attr[self._departure]["route"]["type"]

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def available(self) -> bool:
        """To be implemented."""
        return True

    @property
    def extra_state_attributes(self):
        return self._extra_attr

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        if int(self._route_type) == 0:
            icon = ICON_TRAM
        elif int(self._route_type) == 1:
            icon = ICON_METRO
        elif int(self._route_type) == 2:
            icon = ICON_TRAIN
        else:
            icon = ICON_BUS
        return icon

    @property
    def name(self):
        return self._attr_name

    async def async_update(self):
        await self._departure_board.async_update()
        self._state = self._departure_board.extra_attr[self._departure]["route"]["short_name"]
        self._extra_attr = self._departure_board.extra_attr[self._departure]


class StopSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

        # The name of the entity
        self._attr_name = f"stop name"
        self._state = self._departure_board.stop_name


    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def available(self) -> bool:
        """To be implemented."""
        return True

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON_STOP

    @property
    def name(self):
        return self._attr_name

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC


class WheelchairSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

        # The name of the entity
        self._attr_name = f"wheelchair"
        self._state = self._departure_board.wheelchair_accessible

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def available(self) -> bool:
        """To be implemented."""
        return True

    @property
    def state(self):
        if int(self._state) == 0:
            state = "unknown"
        elif int(self._state) == 1:
            state = "on"
        elif int(self._state) == 2:
            state = "off"
        else:
            state = "not_provided"
        return state

    @property
    def icon(self):
        return ICON_WHEEL

    @property
    def name(self):
        return self._attr_name

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC


class LatSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

        # The name of the entity
        self._attr_name = f"latitude"
        self._state = self._departure_board.latitude

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def available(self) -> bool:
        """To be implemented."""
        return True

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON_LAT

    @property
    def name(self):
        return self._attr_name

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC


class LonSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

        # The name of the entity
        self._attr_name = f"longitude"
        self._state = self._departure_board.longitude

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def available(self) -> bool:
        """To be implemented."""
        return True

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON_LON

    @property
    def name(self):
        return self._attr_name

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC


class ZoneSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

        # The name of the entity
        self._attr_name = f"zone"
        self._state = self._departure_board.zone

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def available(self) -> bool:
        """To be implemented."""
        return True

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON_ZONE

    @property
    def name(self):
        return self._attr_name

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC


class PlatformSensor(SensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

        # The name of the entity
        self._attr_name = f"platform"
        self._state = self._departure_board.platform

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def available(self) -> bool:
        """To be implemented."""
        return True

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON_PLATFORM

    @property
    def name(self):
        return self._attr_name

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC