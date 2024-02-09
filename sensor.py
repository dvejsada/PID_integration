"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from datetime import timedelta

from .const import ICON_BUS, ICON_TRAM, ICON_METRO,ICON_TRAIN, DOMAIN


SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    departure_board = hass.data[DOMAIN][config_entry.entry_id]
    new_entities = []
    for i in departure_board.departures:
        new_entities.append(DepartureSensor(departure_board.departures[i], departure_board))

    # Add all entities to HA

    async_add_entities(new_entities)


class DepartureSensor(SensorEntity):
    """Sensor for departure."""

    def __init__(self, departure: int, departure_board):

        self._departure = departure
        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure}"

        # The name of the entity
        self._attr_name = f"Departure_{self._departure+1}"
        self._state = self._departure_board.extra_attr[self._departure]["route"]["short_name"]
        self._extra_attr = self._departure_board.extra_attr[self._departure]

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
        if self._departure_board.extra_attr[self._departure]["route"]["type"] == 1:
            icon = ICON_TRAM
        elif self._departure_board.extra_attr[self._departure]["route"]["type"] == 0:
            icon = ICON_METRO
        elif self._departure_board.extra_attr[self._departure]["route"]["type"] == 2:
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

