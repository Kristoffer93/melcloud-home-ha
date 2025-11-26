"""Number entities for MELCloud Home ATW."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
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
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    entities: list[NumberEntity] = []
    for device in coordinator.data.get("devices", []):
        if device.get("type") == "air_to_water" and device.get("capabilities", {}).get("hasHotWater", False):
            entities.append(MELCloudTankSetTemperatureNumber(coordinator, api, device))

    async_add_entities(entities)


class MELCloudTankSetTemperatureNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, api, device: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device = device
        self._device_id = device["id"]
        self._attr_unique_id = f"{self._device_id}_tank_set_temp"
        self._attr_name = f"{device.get('givenDisplayName', 'ATW')} Tank Target"
        caps = device.get("capabilities", {})
        self._attr_min_value = caps.get("minSetTankTemperature", 30)
        self._attr_max_value = caps.get("maxSetTankTemperature", 60)
        self._attr_step = max(1.0, float(caps.get("temperatureIncrement", 1) or 1))

    @property
    def native_value(self) -> float | None:
        for d in self.coordinator.data.get("devices", []):
            if d["id"] == self._device_id:
                for s in d.get("settings", []):
                    if s.get("name") == "SetTankWaterTemperature":
                        try:
                            return float(s.get("value"))
                        except (TypeError, ValueError):
                            return None
        return None

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.get("givenDisplayName", "ATW Heat Pump"),
            "manufacturer": "Mitsubishi Electric",
            "model": "ATW Heat Pump",
        }

    async def async_set_native_value(self, value: float) -> None:
        await self._api.set_atw_state(self._device_id, {"setTankWaterTemperature": int(value)})
        await self.coordinator.async_request_refresh()
