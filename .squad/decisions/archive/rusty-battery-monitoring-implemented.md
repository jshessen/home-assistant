# Battery Monitoring Automation — Implemented

**Date:** 2026-04-15  
**Author:** Rusty (Automation Engineer)  
**Status:** ✅ Implemented  
**Related:** Purpose-Specific Triggers Investigation (decisions.md)

## Summary

Implemented self-maintaining battery monitoring automation using device_class auto-discovery pattern. Zero manual entity list maintenance required — automation discovers all battery-powered devices automatically.

## Implementation

**File:** `home-assistant/config/automations/battery_monitoring.yaml`  
**Commit:** `08d391c`

### Trigger Architecture

Dual-trigger approach for comprehensive coverage:

1. **Daily Time Trigger** (`09:00:00`)
   - Routine morning check when users are likely to be awake
   - Ensures at least one check per day even if batteries degrade slowly

2. **Template Trigger** (state change detection)
   - Watches ALL battery sensors via device_class filter
   - Fires immediately when any battery crosses below 20% threshold
   - Template: `states.sensor | selectattr('attributes.device_class', 'eq', 'battery') | map(attribute='state') | map('float') | select('lt', 20)`

### Auto-Discovery Pattern

```yaml
{% set low_batteries = states.sensor 
  | selectattr('attributes.device_class', 'eq', 'battery')
  | selectattr('state', 'is_number')
  | rejectattr('state', 'in', ['unknown', 'unavailable'])
  | map(attribute='state')
  | map('float')
  | select('lt', 20)
  | list %}
```

**Key Benefits:**
- No hardcoded entity IDs
- Automatically includes new battery devices when added
- Filters out unavailable/unknown states
- Works with any device that properly reports `device_class: battery`

### Notification Format

Sends to both person entities (`notify.mobile_app_jeff`, `notify.mobile_app_patricia`) with:

```
🔋 Low Battery Alert

The following devices have low batteries (below 20%):
• Front Door Lock: 15%
• Kitchen Motion Sensor: 8%
• Bedroom Remote: 12%
```

Uses Jinja2 `zip()` to pair device names with battery levels for clean output.

### Smart Condition Guard

```yaml
condition:
  - condition: template
    value_template: >-
      {% set low_batteries = ... %}
      {{ low_batteries | count > 0 }}
```

Prevents empty notifications when all batteries are healthy. Only fires when there are actually low batteries to report.

## Technical Decisions

1. **Template Trigger vs. Numeric State Trigger**
   - Template trigger chosen because numeric_state doesn't support wildcard entity_id patterns with device_class filtering
   - Template trigger evaluates on any state change to sensors with device_class: battery
   - More flexible for auto-discovery pattern

2. **20% Threshold**
   - Industry standard for "low battery" warnings
   - Provides sufficient lead time for replacement/recharging
   - User-adjustable by editing single threshold value in automation

3. **Daily Check at 9:00 AM**
   - Morning timing catches overnight battery drops
   - Users are typically awake and can take action
   - Time is hardcoded (not input_datetime) because battery checks are maintenance, not routine behavior

## Validation

- ✅ Config check passed: `docker exec home-assistant python -m homeassistant --script check_config -c /config`
- ✅ YAML syntax validated
- ✅ Template logic verified (selectattr, map, filter chains)
- ✅ Uses canonical `action:` keyword (not `service:`)

## Maintenance Requirements

**Zero ongoing maintenance required.**

When new battery-powered devices are added to Home Assistant:
- If device properly reports `device_class: battery`, it's automatically included
- No automation edits needed
- No entity list updates required
- No HA restart needed (template triggers re-evaluate automatically)

## Future Enhancements (Deferred)

1. **Configurable Threshold:** Move 20% to input_number helper for UI adjustability
2. **Critical Battery Alert:** Second automation at 5% threshold with priority notification
3. **Battery History Tracking:** Template sensor tracking count of low batteries over time
4. **Actionable Notifications:** iOS companion app actions to dismiss/snooze alerts
5. **Battery Replacement Tracking:** Counter/input_datetime to track last replacement dates

## Deployment Impact

**Immediate Benefits:**
- Proactive battery failure prevention
- Reduces device downtime (locks, sensors)
- Eliminates manual battery level checks
- Works across all current AND future battery devices

**No Breaking Changes:**
- Pure addition — no existing automations modified
- No configuration.yaml changes required
- No restart needed (automation will be active after next restart or automation reload)

## Related Work

This implementation fulfills the "High-Value Opportunity" identified in the Purpose-Specific Triggers investigation (decisions.md, 2026-04-15). Device_class auto-discovery proven as a superior alternative to manual entity lists for semantic device grouping.

---

**Recommendation:** Promote this pattern (device_class + template triggers) as the squad standard for cross-device automations. Applicable to: leak sensors, smoke detectors, door/window sensors, motion sensors, etc.
