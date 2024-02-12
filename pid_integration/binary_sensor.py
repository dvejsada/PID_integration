"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from datetime import timedelta

from .const import ICON_INFO_ON, DOMAIN, ICON_INFO_OFF, ICON_WHEEL
from homeassistant.const import EntityCategory, STATE_UNKNOWN, STATE_UNAVAILABLE, STATE_ON, STATE_OFF

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    departure_board = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([InfotextBinarySensor(departure_board), WheelchairSensor(departure_board)])


class InfotextBinarySensor(BinarySensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure_board):

        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure_board.conn_num+7}"
        # The name of the entity
        self._attr_name = "infotext"
        self._attr_state = self._departure_board.infotext_state
        self._extra_attr = self._departure_board.infotext_attr


    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def extra_state_attributes(self):
        return self._extra_attr


    @property
    def icon(self):
        if self._attr_state:
            icon = ICON_INFO_ON
        else:
            icon = ICON_INFO_OFF
        return icon


    @property
    def is_on(self):
        return self._attr_state

    @property
    def device_class(self):
        return BinarySensorDeviceClass.PROBLEM

    async def async_update(self):
        self._attr_state = self._departure_board.infotext_state
        self._extra_attr = self._departure_board.infotext_attr


class WheelchairSensor(BinarySensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True
    _attr_icon = ICON_WHEEL
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, departure_board):

        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure_board.conn_num+2}"

        # The name of the entity
        self._attr_name = f"wheelchair"

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._departure_board.board_id)}, "name": self._departure_board.name}

    @property
    def state(self):
        if int(self._departure_board.wheelchair_accessible) == 0:
            state = STATE_UNKNOWN
        elif int(self._departure_board.wheelchair_accessible) == 1:
            state = STATE_ON
        elif int(self._departure_board.wheelchair_accessible) == 2:
            state = STATE_OFF
        else:
            state = STATE_UNAVAILABLE
        return state
