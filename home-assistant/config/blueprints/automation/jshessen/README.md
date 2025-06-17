# iBlinds Device Detection & Management Blueprint

## Overview

A comprehensive Home Assistant blueprint for managing iBlinds Z-Wave devices with enhanced automatic device detection. This blueprint provides full automation control for v2 devices while offering detection and configuration guidance for v3 devices.

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fjshessen%2Fhome-assistant%2Fblob%2Fmain%2Fhome-assistant%2Fconfig%2Fblueprints%2Fautomation%2Fjshessen%2Fiblinds_device_handler.yaml)

[GitHub Link](https://github.com/jshessen/home-assistant/blob/main/home-assistant/config/blueprints/automation/jshessen/iblinds_device_handler.yaml)

## Features

### ✅ iBlinds v2 Support
- **Full Management**: Complete automation control with positioning, calibration, and open/close actions
- **Direction Reversal**: Configurable direction reversal for different mounting orientations
- **Custom Positioning**: Set default open positions and handle custom position commands
- **Robust Control**: Handles stop-before-position logic for reliable operation

### 🔍 iBlinds v3 Detection
- **Smart Detection**: Automatically identifies v3 devices using multiple detection methods
- **Configuration Guidance**: Provides direct links to Z-Wave JS configuration interface
- **Best Practice Recommendations**: Guides users to use native Z-Wave parameters for optimal v3 performance

### 📊 Device Analysis
- **Multi-Device Support**: Manages multiple iBlinds devices in a single automation
- **Version Detection**: Distinguishes between v2, v3, and other devices automatically
- **Comprehensive Reporting**: Optional detailed device reports with manufacturer info and capabilities

### 🔔 Notification System
- **Flexible Notifications**: Multiple notification methods (persistent, logbook, custom services)
- **v3 Detection Alerts**: Automatic notifications when v3 devices are detected
- **Action Confirmations**: Optional notifications for completed actions

## Quick Start

1. **Import the Blueprint**: Copy the blueprint YAML and import it into Home Assistant
2. **Create Automation**: Go to Settings → Automations → Create Automation → Use Blueprint
3. **Select Devices**: Choose your iBlinds cover entities
4. **Configure Settings**: Set default positions and notification preferences
5. **Save & Test**: Save the automation and test with your devices

## Configuration Options

### Device Selection
- **iBlinds Devices**: Select one or more cover/blind entities (supports both v2 and v3)

### v2 Operation Settings
- **Default ON Value**: Position percentage (0-100) for open actions
- **Reverse Direction**: Flip direction for different mounting orientations

### v3 Configuration Guidance
- **Automatic Detection**: Identifies v3 devices and provides configuration links
- **Native Parameter Access**: Direct links to Z-Wave JS configuration interface

### Notification Settings
- **v3 Detection Notifications**: Alert when v3 devices are found
- **Device Detection Reports**: Detailed analysis of all detected devices
- **Notification Methods**: 
  - Persistent Notification
  - Logbook
  - System Log
  - Custom notify services

## Device Detection Logic

The blueprint uses a sophisticated detection system:

1. **Primary Detection**: Model name matching (`v2`, `v3`, `2.0`, `3.0`)
2. **Manufacturer Detection**: HAB/iBlinds manufacturer identification
3. **Capability Fallback**: Uses tilt capability to distinguish v3 from v2
4. **Position Fallback**: Uses position capability to identify v2 devices

## Why Different Handling for v2 vs v3?

- **iBlinds v2**: Best managed through Home Assistant automations with direct position control
- **iBlinds v3**: Optimally configured using 10 native Z-Wave configuration parameters for:
  - Better performance
  - Manufacturer-intended operation
  - Reduced conflicts
  - Enhanced reliability

## Supported Actions

### For iBlinds v2 Devices
- `cover.open_cover`: Opens to configured default position
- `cover.close_cover`: Closes completely (respects direction reversal)
- `cover.set_cover_position`: Sets to specific position with direction logic

### For iBlinds v3 Devices
- **Detection Only**: Identifies devices and provides configuration guidance
- **Z-Wave Configuration**: Direct links to native parameter configuration

## Z-Wave JS Configuration Parameters (v3)

The blueprint provides guidance for these v3 parameters:

1. **Close Interval** (1-32): Auto calibration tightness
2. **Reverse Direction** (0/1): Reverse open/close direction
3. **Default ON Position** (1-99): Default open position
4. **Device Reset Disable** (0/1): Disable/enable reset button
5. **Speed** (0-100): Closing speed in seconds
6. **Remote Calibration** (0/1): Trigger recalibration
7. **Min Tilt** (0-25): Minimum tilt level limit
8. **Max Tilt** (75-99): Maximum tilt level limit
9. **Remap 99** (0/1): Remap ON command behavior
10. **Override Response to ON Command** (0/1): Use default instead of 99

## Troubleshooting

### Common Issues

**Q: My v2 blinds move in the wrong direction**
A: Enable "Reverse Direction" in the v2 settings section

**Q: v3 devices aren't being controlled**
A: This is expected - configure v3 devices via Z-Wave JS native parameters for best results

**Q: Device not detected as iBlinds**
A: Check if the device manufacturer contains "HAB" or model contains version numbers

**Q: Notifications not working**
A: Verify your notification service is correctly configured and accessible

### Device Detection Issues

If devices aren't detected properly:
1. Check the device's manufacturer and model in Device Settings
2. Enable "Device Detection Report" for detailed analysis
3. Verify the device is a cover entity with device_class: blind

## Blueprint YAML

[iblinds_device_handler.yaml](https://github.com/jshessen/home-assistant/blob/main/home-assistant/config/blueprints/automation/jshessen/iblinds_device_handler.yaml)

## Installation

### Method 1: Import URL
1. Go to Settings → Automations & Scenes → Blueprints
2. Click "Import Blueprint"
3. Paste the blueprint URL or raw YAML
4. Click "Preview" then "Import"

### Method 2: Manual Import
1. Copy the complete blueprint YAML
2. Go to Settings → Automations & Scenes → Blueprints
3. Click "Import Blueprint"
4. Paste the YAML code
5. Click "Preview" then "Import"

## Usage Examples

### Basic Setup
```yaml
# Minimal configuration for v2 devices
iblinds_entities: 
  - cover.bedroom_blinds
  - cover.living_room_blinds
default_on_value: 75
reverse_direction: false
```

### Advanced Setup
```yaml
# Full configuration with notifications
iblinds_entities:
  - cover.bedroom_blinds_v2
  - cover.office_blinds_v3
default_on_value: 50
reverse_direction: true
notify_v3_detection: true
device_detection_report: true
notification_service_predefined: "persistent_notification.create"
```

## Contributing

Found an issue or have a suggestion? Please:
1. Test thoroughly with your specific iBlinds devices
2. Check existing issues in the Home Assistant community
3. Provide device model/version information
4. Include relevant logs and error messages

## References

- [Home Assistant Community: iBlinds Discussions](https://community.home-assistant.io/search?q=iblinds)
- [Z-Wave JS Device DB - iBlinds v2](https://devices.zwave-js.io/?jumpTo=0x0287:0x0003:0x000d:0.0)
- [Z-Wave JS Device DB - iBlinds v3](https://devices.zwave-js.io/?jumpTo=0x0287:0x0004:0x0071:0.0)
- [iBlinds v3 Configuration Parameters](https://support.myiblinds.com/knowledge-base/configuration-parameters-settings-v3/)

## License

This blueprint is provided as-is for the Home Assistant community. Feel free to modify and distribute according to your needs.

---

## Changelog

### Version 1.0.0
- Initial release
- Full v2 device management
- v3 device detection and guidance
- Comprehensive notification system
- Multi-device support
- Advanced device analysis

## Support

For support and questions:
- Home Assistant Community Forums
- [GitHub Issues](https://github.com/jshessen/home-assistant/issues)
