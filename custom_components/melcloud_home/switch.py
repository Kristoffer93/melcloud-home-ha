"""Switch entity for forced hot water mode."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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

    entities: list[SwitchEntity] = []
    for device in coordinator.data.get("devices", []):
        if device.get("type") == "air_to_water":
            entities.append(MELCloudForcedHotWaterSwitch(coordinator, api, device))

    async_add_entities(entities)


class MELCloudForcedHotWaterSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, api, device: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device = device
        self._device_id = device["id"]
        self._attr_unique_id = f"{self._device_id}_forced_hot_water"
        self._attr_name = f"{device.get('givenDisplayName', 'ATW')} Forced Hot Water"

    @property
    def is_on(self) -> bool:
        for d in self.coordinator.data.get("devices", []):
            if d["id"] == self._device_id:
                for s in d.get("settings", []):
                    if s.get("name") == "ForcedHotWaterMode":
                        return str(s.get("value")) == "True"
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._api.set_atw_state(self._device_id, {"forcedHotWaterMode": True})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._api.set_atw_state(self._device_id, {"forcedHotWaterMode": False})
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.get("givenDisplayName", "ATW Heat Pump"),
            "manufacturer": "Mitsubishi Electric",
            "model": "ATW Heat Pump",
        }
