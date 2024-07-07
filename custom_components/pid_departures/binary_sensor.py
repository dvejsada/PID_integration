"""Platform for binary sensor."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ICON_INFO_ON, DOMAIN, ICON_INFO_OFF, ICON_WHEEL
from .hub import DepartureBoard

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Add sensors for passed config_entry in HA."""
    departure_board: DepartureBoard = hass.data[DOMAIN][config_entry.entry_id]  # type: ignore[Any]
    async_add_entities([WheelchairSensor(departure_board), InfotextBinarySensor(departure_board)])


class InfotextBinarySensor(BinarySensorEntity):
    """Sensor for info text."""
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure_board: DepartureBoard) -> None:

        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure_board.conn_num+7}"

    @property
    def device_info(self) -> DeviceInfo:
        """Returns information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def name(self) -> str:
        """Returns entity name"""
        return "infotext"

    @property
    def is_on(self) -> bool | None:
        return self._departure_board.info_text[0]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return self._departure_board.info_text[1]

    @property
    def icon(self) -> str:
        if self._attr_state:
            return ICON_INFO_ON
        else:
            return ICON_INFO_OFF

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._departure_board.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._departure_board.remove_callback(self.async_write_ha_state)


class WheelchairSensor(BinarySensorEntity):
    """Sensor for wheelchair accessibility of the station."""
    _attr_has_entity_name = True
    _attr_icon = ICON_WHEEL
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, departure_board: DepartureBoard) -> None:

        self._departure_board = departure_board
        self._attr_unique_id = f"{self._departure_board.board_id}_{self._departure_board.conn_num+8}"

    @property
    def device_info(self) -> DeviceInfo:
        """Returns information to link this entity with the correct device."""
        return self._departure_board.device_info

    @property
    def name(self) -> str:
        """Returns entity name"""
        return "wheelchair"

    @property
    def is_on(self) -> bool | None:
        if self._departure_board.wheelchair_accessible == 1:
            return True
        elif self._departure_board.wheelchair_accessible == 2:
            return False
        else:
            return None
