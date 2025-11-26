"""Config flow för MELCloud Home."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .api import MelCloudHomeCookieAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Schema för användarnamn/lösenord
DATA_SCHEMA_LOGIN = vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
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
        """Hantera inloggning med användarnamn och lösenord."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            try:
                # Testa inloggningen
                api = MelCloudHomeCookieAPI()
                await api.async_setup()
                api.set_credentials(username, password)
                
                # Försök logga in
                if not await api.async_login():
                    errors["base"] = "invalid_auth"
                else:
                    # Hämta användarkontext
                    user_context = await api.get_user_context()
                    await api.async_close()
                    
                    if not user_context:
                        errors["base"] = "cannot_connect"
                    else:
                        # Hämta användarnamn för titel
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
                _LOGGER.exception("Oväntat fel vid inloggning")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA_LOGIN,
            errors=errors,
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for MELCloud Home."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - allow updating credentials."""
        errors = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            
            # Validate new credentials
            api = MelCloudHomeCookieAPI()
            await api.async_setup()
            api.set_credentials(username, password)
            
            if await api.async_login():
                user_context = await api.get_user_context()
                await api.async_close()
                
                if user_context:
                    # Update config entry with new credentials
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data={
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                        },
                    )
                    
                    # Clear any session expiration notifications
                    await self.hass.services.async_call(
                        "persistent_notification",
                        "dismiss",
                        {"notification_id": f"{DOMAIN}_session_expired"},
                    )
                    
                    return self.async_create_entry(title="", data={})
                else:
                    errors["base"] = "cannot_connect"
            else:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="init",
            data_schema=DATA_SCHEMA_LOGIN,
            errors=errors,
        )
