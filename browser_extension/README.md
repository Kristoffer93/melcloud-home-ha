# MELCloud Home Cookie Extractor - Browser Extension

Chrome/Firefox extension för att enkelt extrahera cookies från MELCloud Home.

## Installation

### Chrome/Edge

1. Öppna `chrome://extensions/`
2. Aktivera "Developer mode" (uppe till höger)
3. Klicka "Load unpacked"
4. Välj mappen `browser_extension`
5. Extensionen är nu installerad!

### Firefox

1. Öppna `about:debugging#/runtime/this-firefox`
2. Klicka "Load Temporary Add-on"
3. Välj `manifest.json` i `browser_extension` mappen
4. Extensionen är nu installerad!

## Användning

1. Gå till [melcloudhome.com](https://melcloudhome.com) och logga in
2. Klicka på extension-ikonen i verktygsfältet
3. Klicka "Hämta Cookie"
4. Klicka "Kopiera Cookie"
5. Klistra in i Home Assistant när du konfigurerar integrationen

## Säkerhet

- Extensionen har endast åtkomst till cookies från `melcloudhome.com`
- Cookies sparas lokalt i extensionens storage
- Ingen data skickas till externa servrar

## Support

Om du får problem:
- Se till att du är inloggad på melcloudhome.com
- Kontrollera att extensionen har cookie-behörighet
- Öppna Console (F12) för felsökningsloggar
