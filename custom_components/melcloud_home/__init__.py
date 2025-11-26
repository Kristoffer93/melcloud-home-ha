"""MELCloud Home integration för Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MelCloudHomeCookieAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CLIMATE, Platform.SENSOR, Platform.NUMBER, Platform.SWITCH, Platform.SELECT]
SCAN_INTERVAL = timedelta(minutes=15)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Konfigurera MELCloud Home från en config entry."""
    api = MelCloudHomeCookieAPI()
    await api.async_setup()
    
    # Hämta användarnamn/lösenord
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    
    if not username or not password:
        _LOGGER.error("Användarnamn eller lösenord saknas i konfigurationen")
        raise ConfigEntryNotReady("Ingen inloggningsinformation konfigurerad")
    
    # Automatisk inloggning
    _LOGGER.debug("Använder automatisk inloggning med användarnamn/lösenord")
    api.set_credentials(username, password)
    
    if not await api.async_login():
        _LOGGER.error("Kunde inte logga in med användarnamn och lösenord")
        raise ConfigEntryAuthFailed("Inloggning misslyckades")
    
    # Testa anslutningen
    user_context = await api.get_user_context()
    if not user_context:
        _LOGGER.error("Kunde inte verifiera autentisering")
        raise ConfigEntryAuthFailed("Autentisering misslyckades")
    
    # Skapa coordinator
    coordinator = MELCloudHomeCoordinator(hass, api, entry)
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

    def __init__(self, hass: HomeAssistant, api: MelCloudHomeCookieAPI, entry: ConfigEntry) -> None:
        """Initiera coordinatorn."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.entry = entry
        self._failed_updates = 0
        self._cookie_invalid_notified = False

    async def _async_update_data(self) -> dict:
        """Hämta data från API."""
        try:
            # Om vi har användarnamn/lösenord, försök logga in igen vid behov
            username = self.entry.data.get(CONF_USERNAME)
            password = self.entry.data.get(CONF_PASSWORD)
            
            # Hämta användarkontext
            user_context = await self.api.get_user_context()
            
            # Om vi fick 401 och har credentials, försök logga in igen
            if not user_context and username and password:
                _LOGGER.info("Session utgången, försöker logga in igen...")
                if await self.api.async_login():
                    user_context = await self.api.get_user_context()
            
            if not user_context:
                self._failed_updates += 1
                
                # Efter 3 misslyckade försök, skicka notifikation
                if self._failed_updates >= 3 and not self._cookie_invalid_notified:
                    self._cookie_invalid_notified = True
                    
                    message = (
                        "🔐 **MELCloud Home - Session utgången**\n\n"
                        "Din session har upphört. Integrationen kommer försöka logga in "
                        "automatiskt vid nästa uppdatering. Om problemet kvarstår, "
                        "uppdatera dina inloggningsuppgifter under Konfigurera."
                    )
                    
                    # Skapa persistent notifikation
                    await self.hass.services.async_call(
                        "persistent_notification",
                        "create",
                        {
                            "notification_id": f"{DOMAIN}_session_expired",
                            "title": "MELCloud Home - Session utgången",
                            "message": message,
                        },
                    )
                    _LOGGER.warning(
                        "Session har gått ut efter %d misslyckade försök",
                        self._failed_updates
                    )
                
                raise UpdateFailed("Kunde inte hämta användarkontext - session ogiltig?")
            
            # Reset räknare vid lyckad uppdatering
            if self._failed_updates > 0:
                _LOGGER.info("Anslutning återställd efter %d misslyckade försök", self._failed_updates)
                # Rensa notifikation
                await self.hass.services.async_call(
                    "persistent_notification",
                    "dismiss",
                    {"notification_id": f"{DOMAIN}_session_expired"},
                )
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
