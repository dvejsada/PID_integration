"""Platform for binary sensor."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ICON_INFO_ON, ICON_INFO_OFF, ICON_WHEEL
from .coordinator import PIDConfigEntry
from .entity import BaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PIDConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Add sensors for passed config_entry in HA."""
    coordinator = config_entry.runtime_data
    async_add_entities([WheelchairSensor(coordinator), InfotextBinarySensor(coordinator)])


class InfotextBinarySensor(BaseEntity, BinarySensorEntity):
    """Sensor for info text."""

    _attr_translation_key = "infotext"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.info_text[0]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return self.coordinator.info_text[1]

    @property
    def icon(self) -> str:
        if self.is_on:
            return ICON_INFO_ON
        return ICON_INFO_OFF


class WheelchairSensor(BaseEntity, BinarySensorEntity):
    """Sensor for wheelchair accessibility of the station."""

    _attr_translation_key = "wheelchair_accessible"
    _attr_icon = ICON_WHEEL
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.wheelchair_accessible == 1:
            return True
        elif self.coordinator.wheelchair_accessible == 2:
            return False
        else:
            return None
