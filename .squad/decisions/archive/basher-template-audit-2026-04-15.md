# Template Audit for HA 2026.4 Functions
**Date:** 2026-04-15  
**Auditor:** Basher (Template Dev)  
**HA Version:** 2026.4.2  
**Status:** Complete — No changes required

## Executive Summary

Audited all templates across the Home Assistant deployment for opportunities to use new HA 2026.4 template functions:
- `entity_name(entity_id)` — gets friendly name from entity ID
- `state_attr_translated(entity, attr)` — returns human-readable values for HVAC modes, fan speeds, etc.

**Result:** No instances found requiring conversion. Deployment already uses idiomatic HA patterns that don't need migration.

## Function Availability Confirmation

Both functions are **confirmed available** in HA 2026.4.2:

```python
# Verified via Python inspection:
entity_name(hass: 'HomeAssistant', entity_id: 'str') -> 'str | None'
# Docstring: "Get the name of an entity from its entity ID."

# Both exposed as:
# - Template functions: entity_name('sun.sun')
# - Jinja2 filters: 'sun.sun' | entity_name
```

## Audit Scope

**Files Scanned:** 32 YAML files across 4 directories:
- `home-assistant/config/templates/` — 10 files
- `home-assistant/config/packages/` — 6 files
- `home-assistant/config/scripts/` — 12 files
- `home-assistant/config/automations/` — 4 files

**Patterns Searched:**
1. `state_attr(entity, 'friendly_name')` — direct attribute access
2. `states[entity].attributes.friendly_name` — dictionary access
3. `state_attr(entity, "friendly_name")` — double-quote variant
4. `.attributes['friendly_name']` — bracket notation
5. HVAC/climate patterns: `hvac_mode`, `fan_mode`, `preset_mode`, `hvac_action`, `swing_mode`
6. Manual translation maps (hardcoded mode strings → human-readable names)

## Findings

### Pattern 1: `state_attr(entity, 'friendly_name')` ❌
**Instances found:** 0  
**Replacement needed:** N/A

### Pattern 2: `.attributes.friendly_name` ❌
**Instances found:** 0  
**Replacement needed:** N/A

### Pattern 3: `map(attribute='name')` in battery_monitoring.yaml ✅
**File:** `automations/battery_monitoring.yaml`  
**Lines:** 60, 93  
**Pattern:**
```yaml
{% set low_names = states.sensor 
  | selectattr('attributes.device_class', 'eq', 'battery')
  | selectattr('state', 'is_number')
  | rejectattr('state', 'in', ['unknown', 'unavailable'])
  | map(attribute='name')
  | list %}
```

**Analysis:** This pattern uses `map(attribute='name')` which accesses the `name` attribute on state objects. This IS equivalent to getting the friendly name, but:
- **Idiomatic HA pattern** — widely used across community code
- **Semantically clear** — obvious what `.name` does in context
- **Chain-friendly** — works naturally in selectattr/map pipelines
- **No performance benefit** from converting to `entity_name()`

**Decision:** **NO CHANGE** — Current pattern is the correct idiomatic approach for this use case. The `entity_name()` function is designed for when you have an entity_id string and need to get the name in isolation, NOT for filtering/mapping pipelines.

### Pattern 4: HVAC/Climate Mode Attributes ❌
**Instances found:** 0  
**Analysis:** No climate entities or HVAC mode templates exist in the deployment. No opportunity to use `state_attr_translated()`.

### Pattern 5: Manual Translation Maps ⚠️
**Files with maps:** 4 (seasonal templates)  
**Pattern type:** Icon mappings for seasons (NOT HVAC modes)

Example from `templates/seasonal_displays.yaml`:
```yaml
icon: >
  {% set season = states('input_select.active_holiday') %}
  {{ {
    'Halloween': 'mdi:halloween',
    'Thanksgiving': 'mdi:turkey',
    'Christmas': 'mdi:string-lights',
    # ...
  }.get(season, 'mdi:power-socket-us') }}
```

**Analysis:** These are **custom domain-specific mappings** (holidays → icons), NOT HA state attribute translations. `state_attr_translated()` doesn't apply here — it's for translating HA's internal state values (like "heat" → "Heating") to user-facing strings in the UI language.

**Decision:** **NO CHANGE** — Custom business logic, not state translation.

## Out-of-Scope: Blueprints

**Found:** `blueprints/automation/jshessen/iblinds_device_handler.yaml` contains 7 instances of `state_attr(entity, 'friendly_name')`

**Decision:** **Excluded from audit** per task scope:
- Scope explicitly covered: `templates/`, `packages/`, `scripts/`, `automations/`
- Blueprints are reusable automation templates, not deployment-specific configs
- Blueprint changes should be evaluated separately for backward compatibility with older HA versions

If blueprint modernization is desired, open a separate task.

## Conclusion

**No template changes required.** The deployment uses modern, idiomatic Home Assistant patterns:
- No legacy `state_attr(entity, 'friendly_name')` calls in scope
- `map(attribute='name')` is the correct approach for pipelines
- No HVAC/climate entities requiring `state_attr_translated()`
- Custom translation maps are domain-specific logic, not state translations

## Recommendations

1. **Monitor future climate integration** — If HVAC/thermostat devices are added, consider `state_attr_translated()` for user-facing mode displays
2. **Blueprint audit** — Consider separate task to modernize blueprints if they're actively maintained
3. **Document new functions** — Add to project docs if team creates new templates with name/translation needs

## References

- Yen Tech Briefing (2026-04-15) — Action Item 1
- HA 2026.4 Release Notes (assumed source of function announcements)
- HA Template Documentation: https://www.home-assistant.io/docs/configuration/templating/
