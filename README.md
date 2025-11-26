# MELCloud Home Integration för Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/Kristoffer93/melcloud-home-ha.svg)](https://github.com/Kristoffer93/melcloud-home-ha/releases)
[![License](https://img.shields.io/github/license/Kristoffer93/melcloud-home-ha.svg)](LICENSE)

Cookie-baserad integration för MELCloud Home som stödjer:
- 🌡️ **Air-to-Water värmepumpar** (ATW)
- ❄️ **Air-to-Air luftvärmepumpar** (ATA) - kommande
- 🔥 **Temperaturkontroll**
- 💧 **Varmvattentemperatur**
- 📊 **Realtidsdata från enheter**

## Installation

### HACS (Rekommenderat)

1. Öppna HACS i Home Assistant
2. Gå till **Integrations**
3. Klicka på menyn (⋮) uppe till höger
4. Välj **Custom repositories**
5. Lägg till: `https://github.com/Kristoffer93/melcloud-home-ha`
6. Kategori: **Integration**
7. Klicka **Add**
8. Sök efter "MELCloud Home"
9. Klicka **Download**
10. Starta om Home Assistant

### Manuell installation

1. Ladda ner senaste versionen från [Releases](https://github.com/Kristoffer93/melcloud-home-ha/releases)
2. Packa upp och kopiera `custom_components/melcloud_home` till din `config/custom_components/` mapp
3. Starta om Home Assistant

## Konfiguration

### 1. Extrahera Cookie från MELCloud Home

#### Alternativ A: Använd Cookie Helper (Enklare)
1. Öppna `custom_components/melcloud_home/cookie_helper.html` i din webbläsare
2. Följ stegen på sidan för att extrahera cookien

#### Alternativ B: Manuell extraktion
1. Logga in på [melcloudhome.com](https://melcloudhome.com) i Chrome
2. Öppna Developer Tools (F12)
3. Gå till **Network** tab
4. Ladda om sidan (F5)
5. Klicka på första requesten
6. Under **Request Headers**, hitta `cookie:`
7. Högerklicka på värdet → **Copy value**

### 2. Lägg till Integration

1. Gå till **Inställningar** → **Enheter & Tjänster**
2. Klicka **+ LÄGG TILL INTEGRATION**
3. Sök efter **MELCloud Home**
4. Klistra in cookie-strängen
5. Klicka **Skicka**

## Funktioner

### Climate Platform
- `climate.<enhetsnamn>` - Kontrollera din värmepump
  - Sätt måltemperatur (20-50°C)
  - Växla mellan uppvärmning/kylning/av
  - Se aktuell rumstemperatur

### Sensor Platform
- `sensor.<enhetsnamn>_rumstemperatur` - Aktuell rumstemperatur
- `sensor.<enhetsnamn>_varmvattentemperatur` - Varmvattentemperatur

### Extra Attribut
Climate-entiteten har extra attribut:
- `tank_water_temperature` - Varmvattentemperatur
- `set_tank_temperature` - Måltemperatur varmvatten
- `operation_mode_zone1` - Driftläge zon 1
- `forced_hot_water` - Tvingad varmvattenproduktion
- `building` - Byggnadsnamn

## Felsökning

### Cookie har gått ut
Cookies från MELCloud Home har begränsad livstid. Om integrationen slutar fungera:
1. Extrahera ny cookie enligt instruktionerna ovan
2. Gå till **Inställningar → Enheter & Tjänster**
3. Klicka på **MELCloud Home**
4. Välj **Konfigurera**
5. Klistra in ny cookie

### Loggning
Aktivera debug-loggning i `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.melcloud_home: debug
```

## Begränsningar

- Kräver manuell cookie-extraktion (ingen automatisk inloggning)
- Cookies måste uppdateras när de går ut
- Endast läs/skriv av enhetsinställningar (inga schemaläggningsfunktioner än)

## Support

- 🐛 [Rapportera buggar](https://github.com/Kristoffer93/melcloud-home-ha/issues)
- 💡 [Föreslå funktioner](https://github.com/Kristoffer93/melcloud-home-ha/issues)
- 📖 [Dokumentation](https://github.com/Kristoffer93/melcloud-home-ha/wiki)

## Licens

MIT License - se [LICENSE](LICENSE) för detaljer

## Tack till

- Mitsubishi Electric för MELCloud Home-plattformen
- Home Assistant-gemenskapen

1. **Kräver Chromium** - Fungerar inte på alla plattformar
2. **Långsam inloggning** - Browser automation tar tid
3. **Ingen cookie-baserad auth** - Varje omstart kräver ny browser-inloggning

## Alternativ

För en mer robust lösning kan cookie-baserad autentisering användas istället (se `melcloud_cookie_test.py` i repot).

## Support

Rapportera problem på [GitHub Issues](https://github.com/Kristoffer93/melcloud-home-ha/issues)
