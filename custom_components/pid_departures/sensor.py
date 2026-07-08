"""Platform for sensor integration."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ICON_STOP, ICON_LAT, ICON_LON, ICON_ZONE, ICON_PLATFORM, ICON_UPDATE, ROUTE_TYPE_ICON, RouteType
from .coordinator import PIDConfigEntry, PIDDepartureUpdateCoordinator
from .entity import BaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PIDConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Add sensors for passed config_entry in HA."""
    coordinator = config_entry.runtime_data
    new_entities: list[Entity] = []

    # Set entities for departures
    for i in range(coordinator.conn_num):
        new_entities.append(RouteNameSensor(coordinator, i))
        new_entities.append(DepartureTimeSensor(coordinator, i))

    # Set diagnostic entities
    new_entities.append(StopSensor(coordinator))
    new_entities.append(LatSensor(coordinator))
    new_entities.append(LonSensor(coordinator))
    new_entities.append(ZoneSensor(coordinator))
    if coordinator.platform != "":
        new_entities.append(PlatformSensor(coordinator))
    new_entities.append(UpdateSensor(coordinator))

    # Add all entities to HA
    async_add_entities(new_entities)


class RouteNameSensor(BaseEntity, SensorEntity):
    """Sensor for departure route name."""

    _attr_translation_key = "route_name"

    def __init__(self, coordinator: PIDDepartureUpdateCoordinator, departure_num: int) -> None:
        super().__init__(coordinator)
        self._departure = departure_num
        self._attr_unique_id = f"{coordinator.board_id}_{self.translation_key}_{departure_num + 1}"
        self._attr_translation_placeholders = {"num": str(departure_num + 1)}

    @property
    def native_value(self) -> str:
        """ Returns name of the route as state."""
        return self.coordinator.departures[self._departure].route_name or "?"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """ Returns dictionary of additional state attributes"""
        # NOTE: When CONF_LATITUDE and CONF_LONGITUDE is included, HASS shows
        #  the entity on the map.
        return {
            **self.coordinator.departures[self._departure].as_dict(),
            CONF_LATITUDE: self.coordinator.latitude,
            CONF_LONGITUDE: self.coordinator.longitude,
        }

    @property
    def icon(self) -> str:
        """Returns entity icon based on the type of route"""
        route_type = self.coordinator.departures[self._departure].route_type
        return ROUTE_TYPE_ICON.get(route_type, ROUTE_TYPE_ICON[RouteType.BUS])


class DepartureTimeSensor(BaseEntity, SensorEntity):
    """Sensor for the next departure time (estimated)."""

    _attr_translation_key = "departure_time"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: PIDDepartureUpdateCoordinator, departure_num: int) -> None:
        super().__init__(coordinator)
        self._departure_num = departure_num
        self._attr_unique_id = f"{coordinator.board_id}_{self.translation_key}_{departure_num + 1}"
        self._attr_translation_placeholders = {"num": str(departure_num + 1)}

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.departures[self._departure_num].departure_time_est

    @property
    def icon(self) -> str:
        """Returns entity icon based on the type of route"""
        route_type = self.coordinator.departures[self._departure_num].route_type
        return ROUTE_TYPE_ICON.get(route_type, ROUTE_TYPE_ICON[RouteType.BUS])


class StopSensor(BaseEntity, SensorEntity):
    """Sensor for stop name."""

    _attr_translation_key = "stop_name"
    _attr_icon = ICON_STOP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str:
        return self.coordinator.stop_name


class LatSensor(BaseEntity, SensorEntity):
    """Sensor for latitude of the stop."""

    _attr_translation_key = "latitude"
    _attr_icon = ICON_LAT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float:
        return self.coordinator.latitude


class LonSensor(BaseEntity, SensorEntity):
    """Sensor for longitude of the stop."""

    _attr_translation_key = "longitude"
    _attr_icon = ICON_LON
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float:
        return self.coordinator.longitude


class ZoneSensor(BaseEntity, SensorEntity):
    """Sensor for zone."""

    _attr_translation_key = "zone"
    _attr_icon = ICON_ZONE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str:
        return self.coordinator.zone


class PlatformSensor(BaseEntity, SensorEntity):
    """Sensor for platform."""

    _attr_translation_key = "platform"
    _attr_icon = ICON_PLATFORM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str:
        return self.coordinator.platform


class UpdateSensor(BaseEntity, SensorEntity):
    """Sensor reporting the time of the last successful API update."""

    _attr_translation_key = "updated"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = ICON_UPDATE
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_updated
