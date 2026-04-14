# Home Mode & Holiday Automation System

## Complete Setup Guide

This system provides comprehensive house mode management, Good Night/Morning routines, and holiday decoration automation for Home Assistant.

> **2026 implementation note:** In this repo, `script.good_night` is the canonical bedtime orchestrator, `script.good_night_by_area` is the reusable manual area helper, `input_boolean.night_mode` is treated primarily as the resulting state, and grouped/template entities such as `cover.living_room_blinds`, `cover.sunroom_blinds_2`, and `switch.pumpkin_patch` should be preferred over raw device members wherever possible.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Installation Steps](#installation-steps)
3. [Device Configuration](#device-configuration)
4. [Testing & Validation](#testing--validation)
5. [Voice Control Setup](#voice-control-setup)
6. [Customization Guide](#customization-guide)
7. [Troubleshooting](#troubleshooting)

---

## System Overview

### Mode Architecture

**Primary Modes** (Mutually Exclusive):

- **Home**: Normal daily operation
- **Away**: Short-term absence (auto-switches to Vacation after 24hrs)
- **Vacation**: Extended absence, special behaviors
- **Guest**: Guest staying over, modified automations

**Secondary Toggles** (Can overlap):

- **Night Mode**: Bedtime behaviors, dimmed lights
- **Movie Mode**: Optimized for watching movies
- **Party Mode**: Disables certain automations, pauses notifications

**Holiday System**:

- **Active Holiday Selector**: Halloween, Thanksgiving, Christmas, Easter, etc.
- **Inside/Outside Decoration Controls**: Separate schedules
- **Named Voice Switches**: "Turkey Tom", "Pumpkin Patch", "Christmas Spirit"

---

## Installation Steps

### Step 1: Verify File Installation

Review the current implementation files in this repo:

```text
/config/
├── configuration.yaml
├── input_select.yaml
├── input_boolean.yaml
├── alexa.yaml
├── scripts/
│   ├── good_night.yaml
│   ├── good_morning.yaml
│   └── ui_scripts.yaml
├── automations/
│   ├── mode_management.yaml
│   ├── holiday_decorations.yaml
│   └── holiday_season_controller.yaml
└── templates/
    └── seasonal_displays.yaml
```

### Step 2: Configure Your Devices

**CRITICAL**: You must update entity IDs to match your actual devices!

#### Edit these files with your device entity IDs

1. **scripts/good_night.yaml**
   - Replace lock entity IDs (search for `lock.touchscreen_deadbolt_front_door`)
   - Replace garage door cover (search for `cover.garage_door`)
   - Replace blind/shade entities (search for `cover.`)
   - Replace TV/media player entities (search for `media_player.`)
   - Replace light entities for each room (search for `light.`)
   - Replace fan entity (search for `fan.`)
   - Replace Alexa device for announcements (search for `media_player.`)

2. **scripts/good_morning.yaml**
   - Replace kitchen light entities
   - Replace blind/shade entities
   - Replace kids' room light entities
   - Replace Alexa device for announcements

3. **templates/seasonal_displays.yaml**
   - Review the template alias switches and grouped seasonal display wrappers
   - Prefer updating the wrapped physical entity mappings there rather than hard-coding extra raw holiday switches into scripts

### Step 3: Check Configuration

```bash
# Run Home Assistant configuration check
docker exec home-assistant python -m homeassistant --script check_config -c /config

# Or use the VS Code task
# Task: Check Home Assistant Config
```

### Step 4: Restart Home Assistant

```bash
# Restart Home Assistant
docker restart home-assistant

# Or use the VS Code task
# Task: Restart Home Assistant
```

### Step 5: Verify Helpers Created

Go to Settings > Devices & Services > Helpers

You should see:

- ✅ House Mode (input_select)
- ✅ Active Holiday (input_select)
- ✅ Night Mode (input_boolean)
- ✅ Movie Mode (input_boolean)
- ✅ Party Mode (input_boolean)
- ✅ Holiday Decorations Inside (input_boolean)
- ✅ Holiday Decorations Outside (input_boolean)
- ✅ Disable Good Morning (input_boolean)
- ✅ Disable Good Night (input_boolean)
- ✅ Disable Holiday Schedules (input_boolean)

---

## Device Configuration

### Device Inventory Template

Use this template to map your devices to the system. Fill in your actual entity IDs.

#### Locks

```yaml
# Front Door: lock.touchscreen_deadbolt_front_door ✅ (Already configured)
# Back Door: lock._______________
# Garage Door Lock: lock._______________
```

#### Garage Doors

```yaml
# Main Garage: cover._______________
```

#### Blinds/Shades

```yaml
# Living Room: cover._______________
# Kitchen: cover._______________
# Master Bedroom: cover._______________
# Guest Room: cover._______________
# Kid Room 1: cover._______________
# Kid Room 2: cover._______________
```

#### TVs/Media Players

```yaml
# Living Room TV: media_player._______________
# Master Bedroom TV: media_player._______________
# Kid Room 1 TV: media_player._______________
# Kid Room 2 TV: media_player._______________
```

#### Lights (by room)

```yaml
# Living Room:
#   - light._______________
#   - light._______________

# Kitchen:
#   - light._______________
#   - light._______________

# Dining Room:
#   - light._______________

# Hallway:
#   - light._______________

# Master Bedroom:
#   - light._______________ (overhead)
#   - light.bedroom_lamps ✅ (Already configured)

# Guest Room/Office:
#   - light._______________

# Kid Room 1:
#   - light._______________

# Kid Room 2:
#   - light._______________
```

#### Fans

```yaml
# Bedroom Fan: fan._______________
```

#### Holiday Decoration Switches

```yaml
# Halloween:
#   - switch._______________ (outside)
#   - switch._______________ (inside)

# Thanksgiving:
#   - switch._______________ (Turkey Tom inflatable)
#   - switch._______________ (other decorations)

# Christmas:
#   - switch._______________ (tree inside)
#   - switch._______________ (lights outside)
#   - switch._______________ (other decorations)

# Easter:
#   - switch._______________ (Easter inflatable)

# July 4th:
#   - switch._______________ (patriotic lights)
```

#### Alexa Devices

```yaml
# Living Room: media_player._______________
# Kitchen: media_player._______________
# Bedroom: media_player._______________
```

---

## Testing & Validation

### Test Good Night Script

1. Go to Developer Tools > Services
2. Select service: `script.good_night`
3. Click "Call Service"
4. Verify:
   - [ ] Alexa announcement plays
   - [ ] Doors lock
   - [ ] Garage closes
   - [ ] Blinds close
   - [ ] TVs turn off
   - [ ] Holiday decorations turn off
   - [ ] Lights turn off (room by room)
   - [ ] Bedroom fan turns on
   - [ ] Night mode enables

### Test Good Morning Script

1. Go to Developer Tools > Services
2. Select service: `script.good_morning`
3. Click "Call Service"
4. Verify:
   - [ ] Night mode disables
   - [ ] Alexa announcement plays
   - [ ] Kitchen lights turn on
   - [ ] Blinds open (gradually)

### Test Holiday Switches

1. Set Active Holiday to "Christmas"
2. Turn on: `switch.christmas_spirit`
3. Verify your Christmas decorations turn on
4. Repeat for other holidays

### Test Mode Changes

1. Change House Mode to "Away"
   - Verify lights turn off
   - Verify doors lock
2. Change House Mode back to "Home"
3. Run `script.good_night` from the dashboard or Developer Tools
   - Verify `input_boolean.night_mode` turns on as the resulting state
4. Enable `Movie Mode`
   - Verify living room lights dim

---

## Voice Control Setup

### Alexa Configuration

1. **Discover Devices in Alexa App**:
   - Open Alexa app
   - Go to Devices > "+" > Add Device
   - Select "Other" and wait for discovery

2. **Create Alexa Routines**:

#### Good Night Routine

```text
Trigger: "Alexa, good night"
Actions:
  1. Smart Home > Run "Good Night" script
```

> Legacy toggle-based routines may still work, but moving forward the preferred manual/voice path is to call `script.good_night` directly.

#### Good Morning Routine

```text
Trigger: "Alexa, good morning"
Actions:
  1. Smart Home > Run "Good Morning" script
```

#### Holiday Decoration Routines

```text
"Alexa, turn on Turkey Tom"
  → Turn on switch.turkey_tom

"Alexa, turn on Pumpkin Patch"
  → Turn on switch.pumpkin_patch

"Alexa, turn on Christmas Spirit"
  → Turn on switch.christmas_spirit
```

#### Mode Control Routines

```text
"Alexa, movie time"
  → Turn on input_boolean.movie_mode

"Alexa, party mode"
  → Turn on input_boolean.party_mode

"Alexa, we're home"
  → Set input_select.house_mode to "Home"

"Alexa, we're leaving"
  → Set input_select.house_mode to "Away"
```

---

## Customization Guide

### Adjust Schedules

Edit automation times in:

- `automations/mode_management.yaml` - Good Night / Good Morning time-based automations
- `automations/holiday_decorations.yaml` and `automations/holiday_season_controller.yaml` - holiday schedules and season selection

#### Example: Change Good Night Time

```yaml
# In automations/mode_management.yaml
- id: good_night_time_weekday
  triggers:
    - trigger: time
      at: "22:30:00"  # Change from 23:00:00 to 10:30 PM
```

### Add More Holidays

1. Add holiday to `input_select.yaml`:

```yaml
active_holiday:
  options:
    # ... existing holidays ...
    - "Valentines Day"
    - "St Patricks Day"
```

1. Add or extend the seasonal template alias in `templates/seasonal_displays.yaml`
2. Add or adjust the relevant automation in `automations/holiday_decorations.yaml` or `automations/holiday_season_controller.yaml`

### Customize Room Behavior

Edit `scripts/good_night.yaml` to:

- Add/remove rooms
- Change light brightness levels
- Add conditional logic for different modes

---

## Troubleshooting

### Scripts Not Running

**Problem**: Good Night script doesn't do anything

**Solutions**:

1. Check entity IDs are correct (all those `TODO` comments!)
2. Check automation conditions (modes, time of day)
3. Check Home Assistant logs: Settings > System > Logs
4. Test script manually from Developer Tools > Services

### Holiday Switches Not Appearing

**Problem**: Named switches (Turkey Tom, etc.) don't show up

**Solutions**:

1. Verify template entities loaded: Developer Tools > States, search for "switch."
2. Check `templates/seasonal_displays.yaml` for syntax errors or outdated wrapped entities
3. Restart Home Assistant
4. Check that placeholder entity IDs are replaced

### Alexa Not Discovering Devices

**Problem**: Alexa can't find new entities

**Solutions**:

1. Verify entities are exposed in `alexa.yaml`
2. Restart Home Assistant
3. In Alexa app: Devices > Discover Devices
4. Wait 30-60 seconds for discovery
5. Check Home Assistant logs for Alexa integration errors

### Automations Not Triggering

**Problem**: Good Night doesn't run at scheduled time

**Solutions**:

1. Check automation conditions (house mode, disable flags)
2. Verify time zone is correct in HA
3. Check if automation is enabled: Settings > Automations
4. Check automation trace: Click automation > 3 dots > Traces

---

## 📝 Next Steps

After basic setup:

1. ✅ **Complete device inventory** - Fill in all entity IDs
2. ✅ **Test each script manually** - Verify behavior
3. ✅ **Adjust schedules** - Match your family's routine
4. ✅ **Set up Alexa routines** - Enable voice control
5. ✅ **Add dashboard** - Use lovelace/mode_dashboard.yaml
6. ✅ **Monitor for a few days** - Tweak as needed

---

## 📚 Additional Resources

- [Home Assistant Input Select](https://www.home-assistant.io/integrations/input_select/)
- [Home Assistant Input Boolean](https://www.home-assistant.io/integrations/input_boolean/)
- [Home Assistant Scripts](https://www.home-assistant.io/integrations/script/)
- [Alexa Smart Home Integration](https://www.home-assistant.io/integrations/alexa.smart_home/)

---

## 🆘 Support

If you encounter issues:

1. Check Home Assistant logs
2. Verify entity IDs match your devices
3. Test scripts manually before relying on automations
4. Review automation traces for debugging

### Happy Automating! 🎉
