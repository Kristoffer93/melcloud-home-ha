"""Climate platform för MELCloud Home."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
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
    """Konfigurera climate-entiteter från en config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    
    entities = []
    devices = coordinator.data.get("devices", [])
    
    # Skapa climate-entiteter för Air-to-Water enheter (värmepumpar)
    for device in devices:
        if device.get("type") == "air_to_water":
            entities.append(MELCloudHomeClimate(coordinator, api, device))
    
    async_add_entities(entities)


class MELCloudHomeClimate(CoordinatorEntity, ClimateEntity):
    """Representation av en MELCloud Home ATW-värmepump."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]

    def __init__(self, coordinator, api, device: dict[str, Any]) -> None:
        """Initiera climate-entiteten."""
        super().__init__(coordinator)
        self._api = api
        self._device = device
        self._device_id = device["id"]
        self._attr_unique_id = f"{self._device_id}_climate"
        self._attr_name = device.get("givenDisplayName", "Värmepump")
        
        # Sätt temperaturlimiter från capabilities
        capabilities = device.get("capabilities", {})
        self._attr_min_temp = capabilities.get("minSetTemperature", 20)
        self._attr_max_temp = capabilities.get("maxSetTemperature", 50)
        self._attr_target_temperature_step = 1.0 if not capabilities.get("hasHalfDegrees") else 0.5

    def _get_setting(self, name: str) -> Any:
        """Hämta värde från settings."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device["id"] == self._device_id:
                for setting in device.get("settings", []):
                    if setting.get("name") == name:
                        value = setting.get("value")
                        # Konvertera strängar till rätt typ
                        if value in ("True", "False"):
                            return value == "True"
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return value
        return None

    @property
    def device_info(self):
        """Returnera enhetsinformation."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._attr_name,
            "manufacturer": "Mitsubishi Electric",
            "model": "ATW Heat Pump",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device["id"] == self._device_id:
                return device.get("isConnected", False)
        return False

    @property
    def current_temperature(self) -> float | None:
        """Returnera nuvarande temperatur."""
        return self._get_setting("RoomTemperatureZone1")

    @property
    def target_temperature(self) -> float | None:
        """Returnera måltemperatur."""
        return self._get_setting("SetTemperatureZone1")

    @property
    def hvac_mode(self) -> HVACMode:
        """Returnera nuvarande HVAC-läge."""
        if not self._get_setting("Power"):
            return HVACMode.OFF
        
        op_mode = self._get_setting("OperationMode")
        if op_mode == "Heating":
            return HVACMode.HEAT
        elif op_mode == "Cooling":
            return HVACMode.COOL
        
        return HVACMode.HEAT

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Returnera extra attribut."""
        return {
            "tank_water_temperature": self._get_setting("TankWaterTemperature"),
            "set_tank_temperature": self._get_setting("SetTankWaterTemperature"),
            "operation_mode_zone1": self._get_setting("OperationModeZone1"),
            "forced_hot_water": self._get_setting("ForcedHotWaterMode"),
            "building": self._device.get("building_name"),
        }

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Sätt ny måltemperatur."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        await self._api.set_atw_state(
            self._device_id,
            {"setTemperatureZone1": int(temperature)}
        )
        
        # Uppdatera coordinator
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Sätt nytt HVAC-läge."""
        state = {}
        
        if hvac_mode == HVACMode.OFF:
            state["power"] = False
        else:
            state["power"] = True
            # Air-to-Water stöder endast värmelägen: HeatRoomTemperature, HeatFlowTemperature, HeatCurve
            # Standard vid påslag: HeatRoomTemperature
            state["operationModeZone1"] = "HeatRoomTemperature"
        
        await self._api.set_atw_state(self._device_id, state)
        
        # Uppdatera coordinator
        await self.coordinator.async_request_refresh()
