"""Sensor platform för MELCloud Home."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Konfigurera sensor-entiteter från en config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    entities = []
    devices = coordinator.data.get("devices", [])
    
    # Skapa sensorer för Air-to-Water enheter
    for device in devices:
        if device.get("type") == "air_to_water":
            device_id = device["id"]
            device_name = device.get("givenDisplayName", "Värmepump")
            
            # Kontrollera vilka sensorer som finns tillgängliga
            settings_dict = {s["name"]: s["value"] for s in device.get("settings", [])}
            
            if "RoomTemperatureZone1" in settings_dict:
                entities.append(
                    MELCloudHomeTemperatureSensor(
                        coordinator, device_id, device_name, "room_temperature",
                        "Rumstemperatur", "RoomTemperatureZone1"
                    )
                )
            
            if "TankWaterTemperature" in settings_dict:
                entities.append(
                    MELCloudHomeTemperatureSensor(
                        coordinator, device_id, device_name, "tank_temperature",
                        "Varmvattentemperatur", "TankWaterTemperature"
                    )
                )
    
    async_add_entities(entities)


class MELCloudHomeTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Temperatursensor för MELCloud Home."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        unit_id: str,
        unit_name: str,
        sensor_type: str,
        sensor_name: str,
        data_key: str,
    ) -> None:
        """Initiera sensorn."""
        super().__init__(coordinator)
        self._unit_id = unit_id
        self._sensor_type = sensor_type
        self._data_key = data_key
        self._attr_unique_id = f"{unit_id}_{sensor_type}"
        self._attr_name = sensor_name

    @property
    def device_info(self):
        """Returnera enhetsinformation."""
        return {
            "identifiers": {(DOMAIN, self._unit_id)},
        }

    @property
    def native_value(self) -> float | None:
        """Returnera sensorvärdet."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device["id"] == self._unit_id:
                for setting in device.get("settings", []):
                    if setting.get("name") == self._data_key:
                        value = setting.get("value")
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return None
        return None
