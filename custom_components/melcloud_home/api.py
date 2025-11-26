"""Cookie-baserad MELCloud Home API-klient."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://melcloudhome.com"


class MelCloudHomeCookieAPI:
    """Cookie-baserad API-klient för MELCloud Home."""

    def __init__(self) -> None:
        """Initiera API-klienten."""
        self._session: aiohttp.ClientSession | None = None
        self._cookie: str | None = None

    async def async_setup(self) -> None:
        """Sätt upp aiohttp-sessionen."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def async_close(self) -> None:
        """Stäng sessionen."""
        if self._session:
            await self._session.close()
            self._session = None

    def set_cookie(self, cookie: str) -> None:
        """Sätt cookie för autentisering."""
        self._cookie = cookie

    async def get_user_context(self) -> dict[str, Any] | None:
        """Hämta användarkontext."""
        if not self._session or not self._cookie:
            return None

        headers = {
            "x-csrf": "1",
            "Cookie": self._cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        try:
            async with self._session.get(
                f"{BASE_URL}/api/user/context", headers=headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    _LOGGER.error("Cookie ogiltig - behöver ny inloggning")
                    return None
                else:
                    _LOGGER.error("API-fel: %s", response.status)
                    return None
        except Exception as err:
            _LOGGER.exception("Fel vid hämtning av användarkontext: %s", err)
            return None

    async def set_atw_state(
        self, unit_id: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Uppdatera inställningar för en ATW-enhet.
        
        Args:
            unit_id: ID för enheten
            state: Flat dictionary med camelCase-nycklar, ex: {"power": true, "setTemperatureZone1": 22}
        """
        if not self._session or not self._cookie:
            return None

        headers = {
            "x-csrf": "1",
            "Cookie": self._cookie,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        try:
            async with self._session.put(
                f"{BASE_URL}/api/atwunit/{unit_id}",
                json=state,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status in (200, 204):
                    return {"success": True}
                else:
                    text = await response.text()
                    _LOGGER.error(
                        "Kunde inte uppdatera ATW-enhet %s: %s - %s", unit_id, response.status, text
                    )
                    return None
        except Exception as err:
            _LOGGER.exception("Fel vid uppdatering av ATW-enhet %s: %s", unit_id, err)
            return None
