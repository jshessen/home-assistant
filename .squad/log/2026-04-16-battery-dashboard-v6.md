# Session Log: Battery Dashboard v6

**Date:** 2026-04-16  
**Participants:** Danny (Lead/Architect), Basher (Template Dev), Rusty (Lovelace Implementor)  
**Status:** ✅ COMPLETE — Config validated, approved by Danny, ready for production

---

## Summary

Battery Dashboard v6 is a complete rewrite of the Monitor view, fixing three architectural bugs introduced in v5. Danny authored the ADR and implementation brief, Basher fixed the Jinja2 fleet count template, and Rusty implemented the full dashboard. Config validation passed.

---

## What Was Wrong (v5 Bugs)

| Bug | Root Cause |
|-----|-----------|
| Fleet count showed 0 Low | Used `*_battery_low` binary sensors — Battery Notes threshold ≈10%, not 40% |
| Area grouping broken | `group_by: area` — invalid parameter in battery-state-card v4.2.0 |
| Needs Attention buckets wrong | `collapse:` with `from:`/`to:` keys — undocumented/ignored |

Additional v5 issues: deprecated `sort_by_level: true`; missing `default_config_base: false` causing shallow-merge collisions.

---

## Key Events

### Danny — ADR + Implementation Brief

Danny filed **ADR-2026-04** (`.squad/decisions/inbox/danny-battery-dashboard-v6-adr.md`) and a companion implementation brief for Rusty and Basher.

**Six binding decisions recorded:**

1. **Dynamic area grouping** via `by: "device.area_name"` — confirmed working via `accessor.resolve()` in v4.2.0 source; explicit per-area fallback documented
2. **Two views retained** — Monitor (operational) vs Manage (replacement workflow) serve distinct use-cases; consolidating would require conflicting sort orders
3. **`default_config_base: false` mandatory** — v4.2.0 defaults corrupt include filter, secondary_info, bulk_rename, and collapse; all cards must disable base
4. **Fleet count via `*_battery_plus` sensors** — binary sensors use per-device threshold (≈10%); only direct float comparison over sensor states is correct
5. **`computed.state` for numeric exclude** — triggers the card's `gt()` / `Number(t)` coercion; raw `state` may fall back to string comparison
6. **`secondary_info` format** — `"{attributes.battery_type_and_quantity} · {attributes.battery_last_replaced|reltime()}"` with graceful ISO fallback

---

### Basher — Fleet Count Template Fix

Basher filed the corrected Jinja2 template (`.squad/decisions/inbox/basher-fleet-count-template.md`).

**Key fixes over Danny's draft:**

| | Danny's Brief | Basher's Fix |
|---|---|---|
| State coercion | `\| float(100)` | `\| float(100)` ✅ (confirmed) |
| `_low` guard | absent | `rejectattr('entity_id', 'search', '_low')` added |

**Why the `_low` guard:** `binary_sensor.*_battery_plus_low` entities exist in the registry. `states.sensor` already excludes them (wrong domain), but the `rejectattr` is defence-in-depth against any future `sensor.*_battery_plus_low` entities.

**Approved template:**
```yaml
content: >
  {% set ns = namespace(total=0, crit=0, low=0) %}
  {% for s in states.sensor
      | selectattr('entity_id', 'search', '_battery_plus')
      | rejectattr('entity_id', 'search', '_low')
      | rejectattr('state', 'in', ['unavailable', 'unknown']) %}
    {%- set v = s.state | float(100) -%}
    {%- set ns.total = ns.total + 1 -%}
    {%- if v < 20 -%}{%- set ns.crit = ns.crit + 1 -%}
    {%- elif v < 40 -%}{%- set ns.low = ns.low + 1 -%}{%- endif -%}
  {% endfor %}
  📊 **Battery Fleet:** {{ ns.total }} monitored
  · 🔴 **{{ ns.crit }}** critical (<20%)
  · 🟡 **{{ ns.low }}** low (20–39%)
  · ✅ **{{ ns.total - ns.crit - ns.low }}** OK
```

---

### Rusty — v6 Implementation

Rusty implemented the full dashboard at `home-assistant/config/lovelace/battery_dashboard.yaml`.

**Structure:**
```
battery_dashboard.yaml
├── View 1: Monitor (battery-monitor)
│   ├── Card 1: Markdown — Fleet summary (Basher-approved Jinja2)
│   ├── Card 2: battery-state-card — All Batteries by Room
│   │   ├── default_config_base: false
│   │   └── group: [{by: "device.area_name"}]
│   └── Card 3: battery-state-card — Needs Attention (<40%)
│       ├── default_config_base: false
│       ├── exclude: computed.state >= 40
│       └── group: [{max: 19}, {min: 20, max: 39}]
└── View 2: Manage (battery-manage)   ← unchanged from v5
    ├── Card 1: auto-entities — Replacement history (oldest first)
    ├── Card 2: auto-entities — Never replaced
    └── Card 3: auto-entities — Log replacement buttons
```

**Config validation:** ✅ Passed  
```bash
docker exec home-assistant python -m homeassistant --script check_config -c /config
```

---

### Danny — Code Review

Danny reviewed the implementation (`.squad/decisions/inbox/danny-v6-review.md`).

**Verdict: ✅ APPROVED**

All 7 checklist items passed:
- `default_config_base: false` present on both battery-state-card instances
- `float(100)` and `rejectattr '_low'` guards confirmed in fleet template
- `group:` uses valid v4.2.0 syntax (`by:` and `min:`/`max:`, no legacy `group_by:`)
- Garage Entry Lock (32%) routes to Low group, not Critical
- `computed.state >= 40` exclude present and correct
- `secondary_info` shows battery type + reltime on both cards
- No legacy `group_by:` or `collapse: from/to` anywhere in file

**Non-blocking note:** All Batteries card uses `value: 20` for the red color step; Needs Attention uses `value: 19`. Recommended fix in next patch (cosmetic, no blocking impact).

---

## Root Causes Fixed

| v5 Bug | Fix Applied |
|--------|------------|
| Fleet count (binary sensor threshold) | Replaced `*_battery_low` counting with direct `float` comparison over `*_battery_plus` sensors |
| Area grouping (`group_by` invalid) | Replaced with `group: [{by: "device.area_name"}]` — valid v4.2.0 syntax |
| Collapse bucketing (`from`/`to` invalid) | Replaced with `group: [{max: 19}, {min: 20, max: 39}]` using valid `min`/`max` keys |

---

## Open Items

- [ ] Post-deploy visual verification checklist (fleet counts, room groups, secondary_info rendering, browser console)
- [ ] Next patch: align All Batteries color step to `value: 19` (cosmetic, non-blocking per Danny review)

---

## Files

| File | Action |
|------|--------|
| `home-assistant/config/lovelace/battery_dashboard.yaml` | Rewritten (Monitor view); Manage view unchanged |
| `.squad/decisions/inbox/danny-battery-dashboard-v6-adr.md` | Merged → decisions.md |
| `.squad/decisions/inbox/danny-battery-v6-brief-for-implementors.md` | Merged → decisions.md |
| `.squad/decisions/inbox/basher-fleet-count-template.md` | Merged → decisions.md |
| `.squad/decisions/inbox/danny-v6-review.md` | Merged → decisions.md |
