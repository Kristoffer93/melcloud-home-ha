"""Config flow för MELCloud Home (Cookie-baserad)."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .api import MelCloudHomeCookieAPI
from .const import CONF_COOKIE, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_COOKIE): str,
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MELCloud Home."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Hantera användarsteget."""
        errors: dict[str, str] = {}

        if user_input is not None:
            cookie = user_input[CONF_COOKIE]

            try:
                # Testa cookien
                api = MelCloudHomeCookieAPI()
                await api.async_setup()
                api.set_cookie(cookie)
                
                user_context = await api.get_user_context()
                await api.async_close()
                
                if not user_context:
                    errors["base"] = "invalid_cookie"
                else:
                    # Hämta användarnamn för titel (data ligger direkt på top-level)
                    firstname = user_context.get("firstname", "")
                    lastname = user_context.get("lastname", "")
                    name = f"{firstname} {lastname}".strip()
                    if not name:
                        name = user_context.get("email", "MELCloud Home")
                    
                    # Skapa entry
                    return self.async_create_entry(
                        title=f"MELCloud Home ({name})",
                        data=user_input,
                    )
                
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Oväntat fel vid verifiering av cookie")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "instructions": (
                    "1. Logga in på https://melcloudhome.com i din webbläsare\n"
                    "2. Öppna Developer Tools (F12)\n"
                    "3. Gå till Console-fliken\n"
                    "4. Kör: document.cookie\n"
                    "5. Kopiera hela cookie-strängen och klistra in här"
                )
            },
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for MELCloud Home."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - allow updating cookie."""
        errors = {}

        if user_input is not None:
            # Validate new cookie
            api = MelCloudHomeCookieAPI()
            await api.async_setup()
            api.set_cookie(user_input[CONF_COOKIE])
            
            user_context = await api.get_user_context()
            await api.async_close()
            
            if user_context:
                # Update config entry with new cookie
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={CONF_COOKIE: user_input[CONF_COOKIE]},
                )
                
                # Clear any cookie expiration notifications
                await self.hass.services.async_call(
                    "persistent_notification",
                    "dismiss",
                    {"notification_id": f"{DOMAIN}_cookie_expired"},
                )
                
                return self.async_create_entry(title="", data={})
            else:
                errors["base"] = "invalid_cookie"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_COOKIE,
                        default=self.config_entry.data.get(CONF_COOKIE, ""),
                    ): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "info": "Uppdatera din MELCloud Home cookie här. "
                "Extrahera en ny cookie från melcloudhome.com (Network tab → Request Headers → cookie)."
            },
        )
