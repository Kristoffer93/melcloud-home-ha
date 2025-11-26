# Release Notes - v1.0.1

## 🐛 Bug Fixes

### HACS Installation Fixed
- **Fixed:** Removed `zip_release` requirement from `hacs.json` that was causing HACS installation to fail with "Could not download" error
- **Impact:** Users can now install the integration directly through HACS without manual installation
- HACS will now download source code directly from GitHub instead of looking for a non-existent zip file

### Translation Improvements
- **Fixed:** Removed duplicate "Varmvattentemperatur" attributes from climate entity
- **Improved:** Clearer entity names in Swedish:
  - "Varmvatten temperatur" (sensor - current temperature)
  - "Varmvatten måltemperatur" (number - target temperature setpoint)
- **Fixed:** Added `translation_key` to all entities for proper localization

### Repository Structure
- Added `icon.png` for better HACS integration visibility
- Added proper GitHub issue templates (bug report, feature request)
- Added pull request template
- Added validation workflow for automated testing
- Added `integration_type: "device"` to manifest.json

---

## 📦 What's Changed

- Removed `tank_water_temperature` and `set_tank_temperature` from climate entity extra attributes (duplicates of dedicated sensor/number entities)
- Updated English translations for better clarity ("Hot Water Target" instead of "Tank Target")
- Improved HACS compatibility configuration

---

## ⬆️ Upgrade Instructions

### From v1.0.0

No breaking changes. Simply update through HACS or manually replace the files.

1. **HACS Update:**
   - Go to HACS → Integrations
   - Find "MELCloud Home"
   - Click "Update"
   - Restart Home Assistant

2. **Manual Update:**
   - Download the latest release
   - Replace the `custom_components/melcloud_home` folder
   - Restart Home Assistant

3. **Reload Integration (Recommended):**
   - Go to Settings → Devices & Services → MELCloud Home
   - Click ⋮ → Reload
   - This will apply the updated translations

---

## 📋 Notes

- This is a patch release focused on bug fixes and HACS compatibility
- No new features added
- All existing configurations remain compatible

---

**Full Changelog:** v1.0.0...v1.0.1
