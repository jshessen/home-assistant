# Hawkeye — History

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

### 2026-04-20: iBlinds Alexa "open" sends to 100% — two compounding bugs found and fixed

**Task:** Explain why Alexa sends v2 blinds to 100% while the iBlinds app correctly opens to 50%.

**Root cause — two compounding bugs:**

**Bug 1 (`_hw` entity bypass):** `packages/iblinds_v2_covers.yaml` correctly renames physical Z-Wave entities to `*_hw` suffix and creates template covers with the original IDs. However, the Alexa config (`cover` domain included, no `*_hw` exclusion) exposes BOTH template covers AND `*_hw` physical entities to Alexa. HA logs confirm this: Alexa sends ChangeReports for `cover.window_blind_controller_2_hw` and `cover.window_blind_controller_4_hw`. When Alexa routes to a `*_hw` entity, `cover.open_cover` on the physical entity → Z-Wave Open (SetLevel 99) → 100%.

**Bug 2 (Alexa bypasses `open_cover` entirely):** For position-aware cover entities, the HA Alexa integration exposes them as `RangeController` (0–100%). "Open the blinds" → Alexa sends `SetRangeValue(100)` → HA calls `cover.set_cover_position(100)`. `open_cover` is never invoked. The template's `set_cover_position` pass-through forwarded 100% unchanged → Z-Wave SetLevel 99 → 100%.

**Why iBlinds app shows 50%:** App uses Bluetooth → Z-Wave SetLevel(50) directly, bypassing HA entirely.

**Fixes applied (2026-04-20):**
1. Created `alexa/exclude/iblinds_hw.yaml` — excludes `cover.*_hw` from Alexa
2. Modified `packages/iblinds_v2_covers.yaml` — all 4 template covers' `set_cover_position` now cap any `position >= 99` to the configured stop point (per-device or global default 50%)
3. HA restart + Alexa device rediscovery required to take effect

**Key pattern learned:** Alexa NEVER calls `cover.open_cover` on position-aware covers. Always test with `set_cover_position(100)` as the Alexa "open" equivalent.

**Decision filed:** `decisions/inbox/livingston-iblinds-alexa.md`

### 2026-04-21: switch.plug_in_front_yard_adapters — entity confirmed valid

**Task:** Verify `switch.plug_in_front_yard_adapters` exists and is functional (Doctor Strange flagged it as backing entity for all 6 seasonal display template switches in `templates/seasonal_displays.yaml`).

**Entity confirmed 🟢:** Present in `core.entity_registry`, platform=`group`, device_class=`outlet`, area=`front_porch`, not disabled.

**Group composition:** 3 Z-Wave JS member switches — `switch.plug_in_outdoor_switch_500s`, `switch.porch_soffit_plug`, `switch.outdoor_double_plug`. All 3 are registered, enabled (disabled_by=None), and on `zwave_js` platform. Group mode is `all: false` (any-on semantics).

**No log errors** found for this entity in `home-assistant.log`.

**Template wiring confirmed correct** — all 6 template switches in `seasonal_displays.yaml` reference the entity properly for state, availability, turn_on, and turn_off.

**Minor cosmetic note:** The 3 member Z-Wave entities have no `area_id` set — doesn't affect function.

**Decision filed:** `decisions/inbox/livingston-front-yard-entity.md`

### 2026-04-20: Comprehensive System Health Check

**Task:** Full health check across all subsystems — HA, Z-Wave, Zigbee2MQTT, Alexa, PostgreSQL, MQTT, Docker.

**Critical finding — Zigbee2MQTT restart loop:**
Root cause is MQTT password mismatch. `zigbee2mqtt/data/configuration.yaml` has `hERCVg2sLAhEiowyQneU` but `config.d/mqtt.env` has `MQTTADMINPW="rk5W6CfqGqiwILv1r22n64mSG3xpky"`. Mosquitto password file was hashed from the env file value. Fix: update zigbee2mqtt config to match mqtt.env password.

**Key pattern for future checks:** When a container is restarting, check `docker logs <container> --tail 50` immediately — even debug-level logs show the exit reason. For Zigbee2MQTT, MQTT auth failures appear as `MQTT failed to connect, exiting... (Connection refused: Not authorized)` in the last lines before shutdown.

**Alexa INVALID_ACCESS_TOKEN:** 135 errors today. These fire in batches when cover entities change state. iBlinds covers ARE alive (triggering ChangeReports); the Alexa skill token is expired/invalid. Re-authentication required — separate from the iblinds position fix.

**MQTT auth diagnostic shortcut:** Mosquitto logs `not authorised` per-connection. Cross-reference the connecting IP against container network assignments to identify the failing client immediately. zigbee2mqtt uses the `172.16.2.0/27` bridge network.

**Z-Wave health:** Node 55 persistently dead. Node 136 generating nonce expiry errors (S0 security timing). Both worth monitoring. Nodes 124 and 138 were removed today — note whether intentional.

**Report filed:** `decisions/inbox/livingston-health-2026-04-20.md`

### 2026-04-21: Full system health audit — MQTT instability root cause, Z-Wave dead lock, z2m false-unhealthy

**Task:** Full health sweep across all 7 subsystems (containers, HA logs, Z-Wave, Zigbee2MQTT, MQTT, PostgreSQL, check_config).

**MQTT instability (W1 — high priority):** 16 MQTT drop events between 10:09–11:48. The `mqtt` container was "Up 27 minutes" at audit time — it restarted ~11:48, correlating precisely with the end of the instability window. System memory spiked to 78% (6300 MB) before the restart and dropped to 38% after — strongly suggests OOM kill. Diagnostic shortcut: `dmesg | grep -i oom` to confirm OOM cause.

**Node 55 = "Back Door Lock" (Sunroom) — dead again (W3 — high priority):** Keymaster logged at HA startup that node 55 is "currently dead." This is the Back Door Lock. Node barely present in registry (only name/loc fields). Battery check and re-pair procedure likely needed.

**Zigbee2MQTT "unhealthy" is a FALSE POSITIVE (W2):** The Docker healthcheck tests `http://localhost:8080/health` — that URL returns 404 because the z2m frontend has no `/health` endpoint. The service is fully operational (MQTT connected, devices publishing). Fix: change healthcheck URL to `/` (root path, returns 200). This has been a persistent false alarm.

**RTL433 sensors flooding WebSocket (W9):** `sensor.citroen_964d6f4f_noise_floor` and `sensor.interlogix_security_140254_signal_snr` caused 3 WebSocket 4096-message backlog events. These SDR sensors update at very high frequency and need to be added to recorder exclude list.

**Alexa token expired (W7):** 3 INVALID_ACCESS_TOKEN errors, affecting `light.bedroom_lamps`, `light.smart_strip_2_1`, `light.smart_strip_1_1`. Auto-refreshes; monitor for persistence.

**Z-Wave:** 47 route failures (nodes 36→50 and 12→48 most affected), 20 duplicate command seq-155 errors, 4 nonce expiry events. Network heal recommended after battery checks on frequently-failing nodes.

**Report filed:** `decisions/inbox/livingston-system-audit-2026-04-21.md`
