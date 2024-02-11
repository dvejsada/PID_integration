"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from datetime import timedelta

from .const import ICON_INFO_ON, DOMAIN, ICON_INFO_OFF


SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    departure_board = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([InfotextBinarySensor(departure_board)])


class InfotextBinarySensor(BinarySensorEntity):
    """Sensor for departure."""
    _attr_has_entity_name = True

    def __init__(self, departure_board):

        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure_board.conn_num+7}"
        # The name of the entity
        self._attr_name = "infotext"
        self._state = self._departure_board.infotext_state
        self._extra_attr = self._departure_board.infotext_attr

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
        if self._state:
            icon = ICON_INFO_ON
        else:
            icon = ICON_INFO_OFF
        return icon

    @property
    def name(self):
        return self._attr_name

    @property
    def is_on(self):
        return self._attr_name

    @property
    def device_class(self):
        return BinarySensorDeviceClass.PROBLEM

    async def async_update(self):
        self._state = self._departure_board.infotext_state
        self._extra_attr = self._departure_board.infotext_attr

