# MELCloud Home Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/Kristoffer93/melcloud-home-ha.svg)](https://github.com/Kristoffer93/melcloud-home-ha/releases)
[![License](https://img.shields.io/github/license/Kristoffer93/melcloud-home-ha.svg)](LICENSE)

> **⚠️ BETA VERSION - USE AT YOUR OWN RISK**
> 
> This integration is currently in beta phase and under active development. I work on it in my spare time and am actively seeking a stable solution, particularly for authentication. **I take no responsibility for any issues that may arise from using this integration.** Use at your own risk.

Cookie-based integration for MELCloud Home supporting:
- 🌡️ **Air-to-Water heat pumps** (ATW)
- ❄️ **Air-to-Air heat pumps** (ATA) - coming soon
- 🔥 **Temperature control**
- 💧 **Hot water temperature**
- 🎛️ **Zone operation modes**
- 📊 **Real-time device data**

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the menu (⋮) in the top right
4. Select **Custom repositories**
5. Add: `https://github.com/Kristoffer93/melcloud-home-ha`
6. Category: **Integration**
7. Click **Add**
8. Search for "MELCloud Home"
9. Click **Download**
10. Restart Home Assistant

### Manual Installation

1. Download the latest version from [Releases](https://github.com/Kristoffer93/melcloud-home-ha/releases)
2. Extract and copy `custom_components/melcloud_home` to your `config/custom_components/` folder
3. Restart Home Assistant

## Configuration

### 1. Extract Cookie from MELCloud Home

1. Log in to [melcloudhome.com](https://melcloudhome.com) in Chrome
2. Open Developer Tools (F12)
3. Go to **Network** tab
4. Reload the page (F5)
5. Click on the first request (melcloudhome.com)
6. Under **Request Headers**, find `cookie:`
7. Right-click on the value → **Copy value**

### 2. Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for **MELCloud Home**
4. Paste the cookie string
5. Click **Submit**

## Features

### Climate Platform
- `climate.<device_name>` - Control your heat pump
  - Set target temperature (20-50°C)
  - Toggle between heat/off
  - View current room temperature

### Sensor Platform
- `sensor.<device_name>_room_temperature` - Current room temperature
- `sensor.<device_name>_hot_water_temperature` - Hot water tank temperature

### Number Platform
- `number.<device_name>_tank_target` - Set hot water tank target temperature (30-60°C)

### Switch Platform
- `switch.<device_name>_forced_hot_water` - Enable/disable forced hot water mode

### Select Platform
- `select.<device_name>_zone_1_mode` - Choose Zone 1 operation mode:
  - Room Thermostat (HeatRoomTemperature)
  - Flow Temperature (HeatFlowTemperature)
  - Heat Curve (HeatCurve)

### Services

#### `melcloud_home.set_tank_water_temperature`
Set the target temperature for the hot water tank.
```yaml
service: melcloud_home.set_tank_water_temperature
data:
  unit_id: "56360d5d-6ab7-4212-9188-9057da1ade8a"
  temperature: 55
```

#### `melcloud_home.set_forced_hot_water`
Enable or disable forced hot water mode.
```yaml
service: melcloud_home.set_forced_hot_water
data:
  unit_id: "56360d5d-6ab7-4212-9188-9057da1ade8a"
  enabled: true
```

#### `melcloud_home.set_operation_mode_zone1`
Set the heating operation mode for Zone 1.
```yaml
service: melcloud_home.set_operation_mode_zone1
data:
  unit_id: "56360d5d-6ab7-4212-9188-9057da1ade8a"
  mode: "HeatRoomTemperature"  # or "HeatFlowTemperature", "HeatCurve"
```

### Extra Attributes
The climate entity includes extra attributes:
- `tank_water_temperature` - Hot water tank temperature
- `set_tank_temperature` - Target hot water temperature
- `operation_mode_zone1` - Zone 1 operation mode
- `forced_hot_water` - Forced hot water mode status
- `building` - Building name

## Troubleshooting

### Cookie Expired
Cookies from MELCloud Home have limited lifespan (typically 1-2 weeks). The integration will automatically notify you after 3 failed API calls.

When notified:
1. Extract a new cookie using the methods above
2. Go to **Settings → Devices & Services**
3. Click on **MELCloud Home**
4. Select **Configure**
5. Paste the new cookie

### Logging
Enable debug logging in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.melcloud_home: debug
```

## Update Interval

The integration polls the MELCloud Home API every **15 minutes** by default. When you make changes (temperature, mode, etc.), the integration immediately requests a fresh update to reflect your changes in the UI.

## Limitations

- Requires manual cookie extraction (no automatic login)
- Cookies must be refreshed when they expire (typically every 1-2 weeks)
- Only read/write device settings (no schedule management yet)
- Air-to-Air (ATA) units not fully supported yet

## Disclaimer

**This is a personal project developed in my spare time.** 

- ⚠️ **No warranty or support guarantees**
- 🔧 **Under active development - expect bugs**
- 🔐 **Authentication solution is still being refined**
- 📝 **Use at your own risk**

I welcome contributions and bug reports, but please understand that responses may be delayed as I work on this when time permits.

## Support

- 🐛 [Report bugs](https://github.com/Kristoffer93/melcloud-home-ha/issues)
- 💡 [Suggest features](https://github.com/Kristoffer93/melcloud-home-ha/issues)
- 📖 [Documentation](https://github.com/Kristoffer93/melcloud-home-ha/wiki)

## License

MIT License - see [LICENSE](LICENSE) for details

## Credits

- Mitsubishi Electric for the MELCloud Home platform
- Home Assistant community

