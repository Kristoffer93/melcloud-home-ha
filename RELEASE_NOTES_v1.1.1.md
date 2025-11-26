# Release Notes - v1.1.1

## 🐛 Bug Fix

### ATA Climate Entity Missing
- **Fixed:** ATA (Air-to-Air) climate entities were not being created due to missing class definition
- **Impact:** Users with ATA heat pumps now get full climate control functionality
- The `MELCloudHomeATAClimate` class was incomplete in v1.1.0, causing only the temperature sensor to appear

---

## ⬆️ Upgrade from v1.1.0

1. Update through HACS or manually replace files
2. Restart Home Assistant
3. **Reload the integration** (Settings → Devices & Services → MELCloud Home → ⋮ → Reload)
4. ATA climate entities will now appear with full controls

---

## 📋 What's Fixed

ATA devices now properly show:
- Climate entity with temperature control (16-31°C)
- Operation modes: Heat, Cool, Auto, Off
- Current and target temperature
- Extra attributes: fan speed, vane positions

---

**Full Changelog:** v1.1.0...v1.1.1
