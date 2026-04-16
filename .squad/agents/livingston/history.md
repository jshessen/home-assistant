# Livingston — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Troubleshooter
- **Joined:** 2026-04-14T17:06:50.078Z

## Learnings

### 2026-04-14: Entity IDs resolved: kitchen lights = light.kitchen_light_3, guest desk lamp = light.guest_outlet_3, persons = person.jeff + person.patricia

Resolved 3 previously TBD entity IDs from entity registry scan. Kitchen cabinet lights map to `light.kitchen_light_3` (only active kitchen light entity; no dedicated under-cabinet entity exists — use at ~10% brightness for pre-dawn). Guest desk lamp maps to `light.guest_outlet_3` (switch_as_x wrapper, not the raw switch entities). Full person entity list confirmed as `person.jeff` and `person.patricia` only. Also identified `light.bedroom_lamps` (main bedroom group) and `light.bedroom_lamps_2` (kids bedroom). No office light entity exists in current registry. Decision filed: `decisions.md`.

### 2026-04-15: iBlinds v2 environment diagnostic — all nodes healthy, blueprint unused

Conducted comprehensive v2 iBlinds analysis (nodes 67, 71, 72, 103, 106, 107). **Findings:** Nodes 71, 72, 103, 107 confirmed active (HAB IB2.0), nodes 67/106 not found in current registry. **Logs clean:** No errors in HA or Z-Wave logs. Confirmed v2 quirk: `targetValue` always reports 99 (cosmetic, doesn't break functionality — `currentValue` shows actual positions correctly). **Blueprint:** Well-designed 509-line automation exists at `blueprints/automation/jshessen/iblinds_device_handler.yaml` with full v2 workarounds (configurable open position, direction reversal, close command mapping) but has **ZERO active automation instances** — it's unused. Scripts (`start_work_day.yaml`, `start_active_day.yaml`, `secure_home.yaml`) reference v2 entities directly via `cover.open_cover` without blueprint intervention. **Entity mapping:** Node 71=`cover.window_blind_controller`, 72=`cover.window_blind_controller_3`, 103=`cover.window_blind_controller_4`, 107=`cover.window_blind_controller_2`. **Conclusion:** v2 environment healthy, blueprint available but not deployed, current setup functional. Filed detailed diagnostic: `decisions/inbox/livingston-iblinds-v2-diagnosis.md`.

### 2026-06-22: iBlinds blueprint deep diagnosis — fatal architecture flaw confirmed

**Task:** Full code review of `blueprints/automation/jshessen/iblinds_device_handler.yaml` to explain why it has never worked.

**PRIMARY FATAL FLAW — Trigger mechanism broken:**
The entire blueprint is built around intercepting `call_service` events (`event_type: call_service`). In HA 2022.4, the `call_service` event was removed from the HA event bus as a performance optimization. Since the deployment is on HA 2026.4.2, these triggers **never fire**. The automation is permanently deaf.

**Secondary issues (would matter if triggers worked):**
1. **`service:` deprecated** — Should be `action:` since HA 2024.8 (cosmetic, still works)
2. **Intercept-and-translate race condition** — Blueprint fires AFTER the original `cover.open_cover` call. Both the HA native open (which v2 can't handle properly) AND the blueprint's `set_cover_position` would execute. Wrong architecture.
3. **`target_entities` returns undefined** — On `automation_reloaded` trigger, `trigger.event.data.service_data` is not defined; the variable template has no else clause and returns `none`
4. **v2 detection logic uncertain** — Primary model-string check ('v2'/'v3' in model) may not match actual Z-Wave model strings; fallback via manufacturer string `'hab' in manufacturer` likely catches `HAB Home Intelligence, LLC` but unverified for this deployment
5. **Recursive Jinja2 macro in variables** — `device_analysis` runs a recursive macro through all selected entities on every trigger fire. Extremely heavy template rendering.

**V2 cover entity IDs confirmed (from entity registry):**
- Node 71 → `cover.window_blind_controller` (Right Blinds)
- Node 72 → `cover.window_blind_controller_3` (Left Blinds)
- Node 103 → `cover.window_blind_controller_4` (Bedroom Blinds)
- Node 107 → `cover.window_blind_controller_2` (Guest Blinds)
- Node 67 → **NO cover entity** (not in registry — device not paired)
- Node 106 → **NO cover entity** (not in registry — device not paired)

**Verdict: REPLACE, not fix.** The design premise (intercepting service calls via events) is permanently broken in modern HA. The correct approach is direct `cover.set_cover_position` automations with explicit v2 entity targets.

**Existing scripts already working around the problem:** `start_work_day.yaml`, `start_active_day.yaml`, `secure_home.yaml` all call `cover.open_cover` directly on v2 entities without going through the blueprint. This works because iBlinds v2 DOES respond to `open_cover` (it opens to 50% by default) — the blueprint's value-add was configurable default position and direction reversal, neither of which is wired up.

**Decision filed:** `decisions/inbox/livingston-iblinds-blueprint-diagnosis.md`
