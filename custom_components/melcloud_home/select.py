"""Select entity for Zone 1 operation mode."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MODES = ["HeatRoomTemperature", "HeatFlowTemperature", "HeatCurve"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    entities: list[SelectEntity] = []
    for device in coordinator.data.get("devices", []):
        if device.get("type") == "air_to_water":
            entities.append(MELCloudOperationModeZone1Select(coordinator, api, device))

    async_add_entities(entities)


class MELCloudOperationModeZone1Select(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_options = MODES

    def __init__(self, coordinator, api, device: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._api = api
        self._device = device
        self._device_id = device["id"]
        self._attr_unique_id = f"{self._device_id}_zone1_mode"
        self._attr_name = f"{device.get('givenDisplayName', 'ATW')} Zone 1 Mode"

    @property
    def current_option(self) -> str | None:
        for d in self.coordinator.data.get("devices", []):
            if d["id"] == self._device_id:
                for s in d.get("settings", []):
                    if s.get("name") == "OperationModeZone1":
                        return str(s.get("value"))
        return None

    async def async_select_option(self, option: str) -> None:
        if option not in MODES:
            _LOGGER.error("Invalid Zone1 mode: %s", option)
            return
        await self._api.set_atw_state(self._device_id, {"operationModeZone1": option})
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.get("givenDisplayName", "ATW Heat Pump"),
            "manufacturer": "Mitsubishi Electric",
            "model": "ATW Heat Pump",
        }
