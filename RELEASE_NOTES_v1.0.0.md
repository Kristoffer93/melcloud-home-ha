# Release Notes - v1.0.0

## 🎉 Major Release: Automatic Authentication

Version 1.0.0 marks a significant milestone with the introduction of automatic authentication, making the integration much easier to use and maintain.

---

## ✨ New Features

### Automatic Login with Username/Password
- **No more manual cookie extraction!** Simply enter your MELCloud Home email and password
- **Automatic session renewal** - the integration re-authenticates automatically when sessions expire (typically every 8 hours)
- **Seamless experience** - users never need to manually refresh credentials unless their password changes

### Simplified Configuration Flow
- Direct login form with username and password
- Removed complex cookie extraction instructions
- One-step setup process

---

## 🔧 Improvements

### Translation Support
- Added `translation_key` to all entities for proper localization
- Full Swedish and English translations for all entity names
- Improved state translations for operation modes:
  - "Rumsgivare" (Room Thermostat)
  - "Flödestemperatur" (Flow Temperature)
  - "Värmekurva" (Heat Curve)

### Code Simplification
- Removed manual cookie authentication flow
- Cleaner API client with automatic session management
- Simplified error handling and notifications

---

## 🐛 Bug Fixes

- Fixed missing translations for Zone 1 operation mode selector
- Fixed translations for number, switch, and sensor entities
- Improved session expiration handling with automatic recovery

---

## 💥 Breaking Changes

### Removed Manual Cookie Authentication
- **Action Required:** Existing installations using manual cookie authentication will need to reconfigure
- The integration now **only** supports username/password authentication
- Users will be prompted to re-enter credentials on next restart

### How to Update from Previous Versions:
1. Remove the existing MELCloud Home integration
2. Restart Home Assistant
3. Re-add the integration with your MELCloud Home email and password
4. All devices and entities will be recreated with the same IDs

---

## 📋 Full Feature List

### Supported Entities
- **Climate** - Temperature control for heat pumps
- **Sensors** - Room temperature, hot water temperature
- **Number** - Hot water tank target temperature (30-60°C)
- **Switch** - Forced hot water mode
- **Select** - Zone 1 operation mode (Room Thermostat/Flow Temperature/Heat Curve)

### Services
- `melcloud_home.set_tank_water_temperature` - Set tank temperature
- `melcloud_home.set_forced_hot_water` - Control forced hot water mode
- `melcloud_home.set_operation_mode_zone1` - Change zone heating mode

---

## 🔐 Security Notes

- Credentials are stored securely in Home Assistant's config entry
- Automatic re-authentication uses the same secure flow as initial login
- Session cookies are handled internally and never exposed to users

---

## 📦 Dependencies

- `aiohttp>=3.8.0` - HTTP client
- `beautifulsoup4>=4.12.0` - HTML parsing for login flow

---

## 🙏 Acknowledgments

Thanks to all beta testers who provided feedback on the authentication flow!

---

## 🐛 Known Issues

- Air-to-Air (ATA) heat pumps not yet fully supported
- Schedule management not yet implemented

---

## 📚 Documentation

- [README](README.md) - Complete setup and usage guide
- [GitHub Issues](https://github.com/Kristoffer93/melcloud-home-ha/issues) - Bug reports and feature requests

---

**Full Changelog:** v0.2.0...v1.0.0
