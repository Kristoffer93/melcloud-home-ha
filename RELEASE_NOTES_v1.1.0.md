# Release Notes - v1.1.0

## ✨ New Features

### Air-to-Air (ATA) Heat Pump Support
- **Added:** Full support for Air-to-Air (ATA) heat pumps / air conditioners
- Climate entity with temperature control (16-31°C)
- Support for Heat, Cool, Auto, and Off modes
- Room temperature sensor
- Extra attributes: operation mode, fan speed, vane position (horizontal/vertical)

**Impact:** Users with ATA units (like indoor air conditioning units) can now fully control them through Home Assistant

---

## ⬆️ Upgrade from v1.0.0

1. Update through HACS or manually replace files
2. Restart Home Assistant
3. **Reload the integration** (Settings → Devices & Services → MELCloud Home → ⋮ → Reload)
4. ATA devices will automatically appear after reload

**Note:** No breaking changes. All existing configurations remain compatible.

---

## 📋 What's New in v1.1.0

- **ATA Support:** New climate class for Air-to-Air units
- **API Method:** New `set_ata_state()` for ATA control
- **Auto-detection:** Both ATW and ATA units are discovered automatically

---

**Full Changelog:** v1.0.0...v1.1.0


