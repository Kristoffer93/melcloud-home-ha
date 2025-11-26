"""MELCloud Home integration för Home Assistant (Cookie-baserad)."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MelCloudHomeCookieAPI
from .const import CONF_COOKIE, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CLIMATE, Platform.SENSOR, Platform.NUMBER, Platform.SWITCH, Platform.SELECT]
SCAN_INTERVAL = timedelta(minutes=15)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Konfigurera MELCloud Home från en config entry."""
    api = MelCloudHomeCookieAPI()
    await api.async_setup()
    
    # Sätt cookie
    cookie = entry.data.get(CONF_COOKIE)
    if not cookie:
        _LOGGER.error("Ingen cookie hittades i konfigurationen")
        raise ConfigEntryNotReady("Ingen cookie konfigurerad")
    
    api.set_cookie(cookie)
    
    # Testa anslutningen
    user_context = await api.get_user_context()
    if not user_context:
        _LOGGER.error("Kunde inte verifiera cookie - ogiltig eller utgången")
        raise ConfigEntryAuthFailed("Cookie ogiltig eller utgången")
    
    # Skapa coordinator
    coordinator = MELCloudHomeCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    
    # Spara i hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }
    
    # Ladda plattformar
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _call_set_state(unit_id: str, state: dict) -> None:
        await coordinator.api.set_atw_state(unit_id, state)
        await coordinator.async_request_refresh()

    async def handle_set_tank_temperature(call):
        unit_id = call.data.get("unit_id")
        temperature = call.data.get("temperature")
        if unit_id is None or temperature is None:
            _LOGGER.error("set_tank_water_temperature requires unit_id and temperature")
            return
        await _call_set_state(unit_id, {"setTankWaterTemperature": int(temperature)})

    async def handle_set_forced_hot_water(call):
        unit_id = call.data.get("unit_id")
        enabled = call.data.get("enabled")
        if unit_id is None or enabled is None:
            _LOGGER.error("set_forced_hot_water requires unit_id and enabled")
            return
        await _call_set_state(unit_id, {"forcedHotWaterMode": bool(enabled)})

    async def handle_set_operation_mode_zone1(call):
        unit_id = call.data.get("unit_id")
        mode = call.data.get("mode")
        if unit_id is None or mode is None:
            _LOGGER.error("set_operation_mode_zone1 requires unit_id and mode")
            return
        await _call_set_state(unit_id, {"operationModeZone1": str(mode)})

    hass.services.async_register(
        DOMAIN,
        "set_tank_water_temperature",
        handle_set_tank_temperature,
    )
    hass.services.async_register(
        DOMAIN,
        "set_forced_hot_water",
        handle_set_forced_hot_water,
    )
    hass.services.async_register(
        DOMAIN,
        "set_operation_mode_zone1",
        handle_set_operation_mode_zone1,
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Avlasta en config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["api"].async_close()
        # Services remain available while any entry is loaded; no per-entry unload needed here.
    
    return unload_ok


class MELCloudHomeCoordinator(DataUpdateCoordinator):
    """Coordinator för att hantera datauppdateringar."""

    def __init__(self, hass: HomeAssistant, api: MelCloudHomeCookieAPI) -> None:
        """Initiera coordinatorn."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self._failed_updates = 0
        self._cookie_invalid_notified = False

    async def _async_update_data(self) -> dict:
        """Hämta data från API."""
        try:
            # Hämta användarkontext som innehåller alla enheter
            user_context = await self.api.get_user_context()
            
            if not user_context:
                self._failed_updates += 1
                
                # Efter 3 misslyckade försök, skicka notifikation
                if self._failed_updates >= 3 and not self._cookie_invalid_notified:
                    self._cookie_invalid_notified = True
                    
                    # Skapa persistent notifikation
                    await self.hass.services.async_call(
                        "persistent_notification",
                        "create",
                        {
                            "notification_id": f"{DOMAIN}_cookie_expired",
                            "title": "MELCloud Home - Cookie utgången",
                            "message": (
                                "🍪 **MELCloud Home Cookie har gått ut**\n\n"
                                "Din cookie-session har upphört att fungera. "
                                "Vänligen extrahera en ny cookie från melcloudhome.com och "
                                "uppdatera integrationen.\n\n"
                                "**Så här gör du:**\n"
                                "1. Gå till Inställningar → Enheter & Tjänster\n"
                                "2. Klicka på MELCloud Home\n"
                                "3. Välj Konfigurera\n"
                                "4. Klistra in ny cookie\n\n"
                                "Eller använd Browser Extension för snabb extraktion."
                            ),
                        },
                    )
                    _LOGGER.warning(
                        "Cookie har gått ut efter %d misslyckade försök. "
                        "Notifikation skickad till användaren.",
                        self._failed_updates
                    )
                
                raise UpdateFailed("Kunde inte hämta användarkontext - cookie ogiltig?")
            
            # Reset räknare vid lyckad uppdatering
            if self._failed_updates > 0:
                _LOGGER.info("Anslutning återställd efter %d misslyckade försök", self._failed_updates)
            self._failed_updates = 0
            self._cookie_invalid_notified = False
            
            # Extrahera enheter från buildings
            devices = []
            for building in user_context.get("buildings", []):
                building_id = building["id"]
                building_name = building["name"]
                
                # Air-to-Water enheter (värmepumpar)
                for atw in building.get("airToWaterUnits", []):
                    atw["type"] = "air_to_water"
                    atw["building_id"] = building_id
                    atw["building_name"] = building_name
                    devices.append(atw)
                
                # Air-to-Air enheter (AC)
                for ata in building.get("airToAirUnits", []):
                    ata["type"] = "air_to_air"
                    ata["building_id"] = building_id
                    ata["building_name"] = building_name
                    devices.append(ata)
            
            return {
                "user_context": user_context,
                "devices": devices,
            }
        except Exception as err:
            self._failed_updates += 1
            raise UpdateFailed(f"Fel vid uppdatering av data: {err}") from err
