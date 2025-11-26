# Images for MELCloud Home Integration

This directory contains images for HACS and documentation.

## Required Images

### icon.png or logo.png
- **Size:** 256x256 px or 512x512 px
- **Format:** PNG with transparent background
- **Purpose:** HACS integration icon
- **Location:** Root directory of repository

### Screenshots (Optional but Recommended)

Screenshots to add to this directory:

1. **config_flow.png** - Configuration flow showing login form
2. **devices.png** - Devices overview in Home Assistant
3. **controls.png** - Entity controls (climate, switches, selectors)
4. **dashboard.png** - Example dashboard with all entities

## How to Create Logo

### Option 1: Use Existing Logo
- Download Mitsubishi Electric logo (check licensing)
- Resize to 256x256 px

### Option 2: Create Custom Icon
Tools:
- Canva (free)
- Figma (free)
- GIMP (free, open source)
- Inkscape (free, open source for SVG)

Suggested design:
- Mitsubishi colors (red #E60012, white)
- Heat pump icon
- House icon
- "MC" or "MELCloud" text

### Option 3: Simple Placeholder
Use Material Design Icons:
- `mdi:heat-pump` 
- `mdi:hvac`
- `mdi:home-thermometer`

## Adding Screenshots

Take screenshots from your Home Assistant installation:
1. Configure the integration (capture login screen)
2. Navigate to Settings → Devices & Services → MELCloud Home
3. Click on a device to see all entities
4. Create a dashboard with climate card, switches, and sensors
5. Take screenshots and save them here

## References

- [HACS Documentation](https://hacs.xyz/docs/publish/integration)
- [Material Design Icons](https://materialdesignicons.com/)
