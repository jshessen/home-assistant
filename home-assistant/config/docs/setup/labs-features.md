# Home Assistant Labs Features

## Overview

Home Assistant Labs is a system for enabling preview/experimental features that are still in development. Labs features are configured through the UI at **Settings → System → Labs**.

## Current Installation Status

**Home Assistant Version:** 2026.4.2

**Labs Configuration Location:** `.storage/core.labs` (JSON file managed by HA)

**Currently Enabled Labs Features:**
- `analytics/snapshots` - Preview feature for analytics snapshots

## Accessing Labs Features

1. Navigate to **Settings** in the Home Assistant UI
2. Select **System**
3. Click **Labs**
4. Toggle preview features on/off as desired

**Note:** Labs features are UI-only configuration. They cannot be enabled via YAML files.

## Research Notes: "Purpose-Specific Triggers" (2026-04-15)

**Context:** Yen's Tech Briefing mentioned "Purpose-Specific Triggers" as a potential HA 2026.4 Labs feature - described as cross-domain semantic triggers (`door opened`, `motion detected`, `battery low`, `occupancy detected`) that work across entity types without needing specific entity IDs.

**Finding:** This feature **does not exist** in Home Assistant 2026.4.2.

### What Actually Exists in HA 2026.4.2

**Available Trigger Types:**
1. **State triggers** (`trigger: state`) - Monitor specific entity state changes
2. **Numeric state triggers** (`trigger: numeric_state`) - Threshold-based monitoring
3. **Time triggers** (`trigger: time`) - Fire at specific times (supports `input_datetime` entities)
4. **Time pattern triggers** (`trigger: time_pattern`) - Cron-like patterns
5. **Event triggers** (`trigger: event`) - Listen to HA events
6. **Homeassistant triggers** (`trigger: homeassistant`) - System events (start, shutdown)

**Device Automation:**
- Integration-specific device triggers exist (Z-Wave, Zigbee, etc.)
- These are device-specific, not cross-domain semantic triggers
- Example: Z-Wave device triggers for button presses, notifications
- Configured via UI (Device Automations) or YAML with `device_id`

### Modern Trigger Patterns Available

While "Purpose-Specific Triggers" don't exist, HA 2026.4 supports these semantic patterns:

#### 1. Label-Based Targeting (Closest to Semantic Triggers)

```yaml
# Turn on all Halloween decorations (cross-domain: switches, lights)
action: switch.turn_on
target:
  label_id: halloween
```

**Use case:** Group entities by purpose rather than domain. Labels can span switches, lights, sensors, etc.

#### 2. Area-Based Actions

```yaml
# Turn off all lights in the bedroom
action: light.turn_off
target:
  area_id: bedroom
```

#### 3. Entity Filtering with Templates

```yaml
# Get all battery sensors below 20%
{% set low_battery = states.sensor
  | selectattr('attributes.device_class', 'eq', 'battery')
  | selectattr('state', 'lt', 20)
  | map(attribute='entity_id')
  | list %}
```

#### 4. Device Class Monitoring

```yaml
# Trigger on any motion sensor
trigger:
  - platform: state
    entity_id: 
      - binary_sensor.kitchen_motion
      - binary_sensor.living_room_motion
    to: 'on'
    attribute: device_class
    value: motion
```

**Note:** Still requires explicit entity lists, but device_class provides semantic meaning.

## Opportunities for Improved Trigger Patterns

Based on current automations in this deployment:

### Opportunity 1: Battery Monitoring with Device Class

**Current approach:** Manual entity lists for battery monitoring
**Modern pattern:** Template sensors that dynamically discover all battery entities

```yaml
# Template sensor for low battery detection
template:
  - binary_sensor:
      - name: "Low Battery Devices"
        state: >
          {{ states.sensor
             | selectattr('attributes.device_class', 'eq', 'battery')
             | selectattr('state', 'is_number')
             | selectattr('state', 'lt', 20)
             | list | count > 0 }}
        attributes:
          devices: >
            {{ states.sensor
               | selectattr('attributes.device_class', 'eq', 'battery')
               | selectattr('state', 'is_number')
               | selectattr('state', 'lt', 20)
               | map(attribute='name')
               | list }}
```

**Then trigger on this single sensor instead of monitoring every battery individually.**

### Opportunity 2: Motion Detection via Labels

**Current approach:** Entity-specific motion triggers
**Modern pattern:** Label all motion sensors, trigger on label

1. Assign `motion_sensor` label to all motion binary_sensors
2. Use in automations:

```yaml
trigger:
  - platform: state
    entity_id: "{{ label_entities('motion_sensor') }}"
    to: 'on'
```

**Benefit:** Adding new motion sensors only requires applying the label, not updating automations.

### Opportunity 3: Occupancy Detection (Cross-Domain)

**Concept:** Combine motion sensors, door sensors, media player state, and presence
**Implementation:** Template binary_sensor for "room occupied"

```yaml
# Occupancy template combining multiple signals
template:
  - binary_sensor:
      - name: "Living Room Occupied"
        state: >
          {{ is_state('binary_sensor.living_room_motion', 'on')
             or is_state('media_player.living_room_tv', 'playing')
             or (is_state('person.jeff', 'home') and now() - states.binary_sensor.living_room_motion.last_changed < timedelta(minutes=30)) }}
```

**Trigger on this semantic sensor instead of individual entities.**

## Recommendations

1. **Use Labels extensively** for cross-domain grouping (holiday decorations already use this pattern)
2. **Create template sensors** for complex semantic states (occupied, low_battery, doors_open)
3. **Leverage device_class** in templates to auto-discover entities by type
4. **Area-based targeting** for location-specific actions

**Future Watch:** If Home Assistant introduces true semantic triggers in future releases, they would likely appear in Labs first. Check Labs settings after major version updates.

## Related Documentation

- [Holiday Automation System](../holidays/HOLIDAY_SYSTEM.md) - Uses label-based triggers
- [Mode Management](../modes/MODE_SYSTEM.md) - Time-based triggers with input_datetime
- [Alexa Integration](../alexa/SMART_HOME_SKILL.md) - Entity filtering patterns

---

**Last Updated:** 2026-04-15  
**Researched By:** Rusty (Automation Engineer)  
**HA Version:** 2026.4.2
