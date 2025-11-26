"""Cookie-baserad MELCloud Home API-klient."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://melcloudhome.com"
LOGIN_START_URL = f"{BASE_URL}/bff/login?returnUrl=/dashboard"


class MelCloudHomeCookieAPI:
    """Cookie-baserad API-klient för MELCloud Home."""

    def __init__(self) -> None:
        """Initiera API-klienten."""
        self._session: aiohttp.ClientSession | None = None
        self._cookie: str | None = None
        self._username: str | None = None
        self._password: str | None = None

    async def async_setup(self) -> None:
        """Sätt upp aiohttp-sessionen."""
        if self._session is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            self._session = aiohttp.ClientSession(headers=headers)

    async def async_close(self) -> None:
        """Stäng sessionen."""
        if self._session:
            await self._session.close()
            self._session = None

    def set_cookie(self, cookie: str) -> None:
        """Sätt cookie för autentisering."""
        self._cookie = cookie

    def set_credentials(self, username: str, password: str) -> None:
        """Sätt användarnamn och lösenord för automatisk inloggning."""
        self._username = username
        self._password = password

    async def async_login(self) -> bool:
        """Logga in med användarnamn och lösenord.
        
        Returns:
            True om inloggningen lyckades, annars False
        """
        if not self._session or not self._username or not self._password:
            _LOGGER.error("Session, användarnamn eller lösenord saknas")
            return False

        try:
            # 1. Hämta inloggningssidan för att få CSRF-token
            _LOGGER.debug("Hämtar inloggningssida...")
            async with self._session.get(LOGIN_START_URL) as resp:
                if resp.status != 200:
                    _LOGGER.error("Kunde inte hämta inloggningssida: %s", resp.status)
                    return False
                
                text = await resp.text()
                final_url = str(resp.url)
                
                if "amazoncognito.com" not in final_url:
                    _LOGGER.warning("Landade inte på Amazon Cognito: %s", final_url)
                    if "dashboard" in final_url:
                        _LOGGER.info("Redan inloggad")
                        return True
                    return False

            # 2. Extrahera CSRF-token
            soup = BeautifulSoup(text, 'html.parser')
            csrf_input = soup.find('input', {'name': '_csrf'})
            
            if not csrf_input:
                _LOGGER.error("Kunde inte hitta CSRF-token")
                return False
            
            csrf_token = csrf_input.get('value')
            _LOGGER.debug("Hittade CSRF-token")

            # 3. Skicka inloggningsuppgifter
            payload = {
                '_csrf': csrf_token,
                'username': self._username,
                'password': self._password,
            }
            
            post_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            async with self._session.post(final_url, data=payload, headers=post_headers) as post_resp:
                final_post_url = str(post_resp.url)
                
                if "dashboard" in final_post_url or post_resp.status == 200:
                    _LOGGER.info("Inloggning lyckades")
                    
                    # Extrahera cookies från sessionen
                    cookies = self._session.cookie_jar.filter_cookies(BASE_URL)
                    cookie_parts = []
                    for cookie in cookies.values():
                        cookie_parts.append(f"{cookie.key}={cookie.value}")
                    
                    self._cookie = "; ".join(cookie_parts)
                    _LOGGER.debug("Sparade %d cookies", len(cookies))
                    return True
                else:
                    _LOGGER.error("Inloggning misslyckades, landade på: %s", final_post_url)
                    return False

        except Exception as err:
            _LOGGER.exception("Fel vid inloggning: %s", err)
            return False

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

    async def set_ata_state(
        self, unit_id: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Uppdatera inställningar för en ATA-enhet (Air-to-Air).
        
        Args:
            unit_id: ID för enheten
            state: Flat dictionary med camelCase-nycklar, ex: {"power": true, "setTemperature": 22}
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
                f"{BASE_URL}/api/ataunit/{unit_id}",
                json=state,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status in (200, 204):
                    return {"success": True}
                else:
                    text = await response.text()
                    _LOGGER.error(
                        "Kunde inte uppdatera ATA-enhet %s: %s - %s", unit_id, response.status, text
                    )
                    return None
        except Exception as err:
            _LOGGER.exception("Fel vid uppdatering av ATA-enhet %s: %s", unit_id, err)
            return None
