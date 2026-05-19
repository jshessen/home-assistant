# ADR-001: iBlinds v2 Stop-Point Fix — Two-Layer Architecture

**Date:** 2026-07-20  
**Status:** Implemented  
**Authors:** Danny (Architect), Linus (Z-Wave), Livingston (Diagnostics), Rusty (Automation Design)

---

## Context

The deployment runs a mixed iBlinds fleet: v2 (firmware 1.65, 6 nodes) and v3 devices. Both generations are Z-Wave covers, but they behave differently when `cover.open_cover` is called:

- **v3**: Uses Z-Wave Parameter 4 ("Default ON Value") to stop at a configured position (e.g. 50%). Works natively.
- **v2 firmware 1.65**: Has **no such parameter**. `cover.open_cover` drives the blind fully to 100%. No Z-Wave config can fix this — it is a firmware limitation.

Additionally, v2 entities showed persistent "unknown" position state in Home Assistant, causing unreliable feedback.

---

## Root Causes Identified

### Problem 1: "Unknown" position (Z-Wave layer)

The `ib2_0.json` device config had no `associations` block. Without a declared Lifeline (Group 1), Z-Wave JS never enrolled the hub as a recipient of unsolicited reports. The hardware supports Association CC v2, but never knew to report back.

### Problem 2: Open command goes to 100% (Firmware limitation)

v2 firmware 1.65 has only one Z-Wave parameter: torque adjustment. There is no parameter analogous to v3's Parameter 4. The stop-point behavior **must** be implemented at the HA layer.

### Problem 3: Broken blueprint (dead code)

The existing `blueprints/automation/jshessen/iblinds_device_handler.yaml` was written to intercept `cover.open_cover` calls via `call_service` events. These events were **removed from the HA event bus in HA 2022.4**. The blueprint has never fired once. It cannot be repaired within its current architecture.

---

## Decision

### Phase 1: Z-Wave Config Fix (Linus — implemented)

**File:** `zwave/.config-db/devices/0x0287/ib2_0.json`

Added:
1. `associations.1` — Lifeline declaration. Z-Wave JS auto-enrolls the hub during re-interview, enabling unsolicited position reports.
2. `compat.treatSetAsReport: ["Multilevel Switch"]` — fw 1.65 may send SET instead of REPORT on the lifeline; this handles the quirk.
3. `compat.commandClasses.remove: Binary Switch` — prevents duplicate cover+switch entities in HA (mirrors the v3 fix).

**Required action:** Re-interview all 6 v2 nodes (67, 71, 72, 103, 106, 107) in Z-Wave JS UI (port 8091) after restarting zwave-js-ui.

### Phase 2: HA Automation Layer — Template Cover Package (this ADR)

**File:** `packages/iblinds_v2_covers.yaml`

**Chosen approach:** Template Covers

**Alternatives evaluated:**

| Approach | Decision | Reason |
|----------|----------|--------|
| Fix the blueprint | ❌ Rejected | `call_service` events don't exist in HA 2022.4+. Not fixable. |
| State-change automation (trigger on `opening`) | ❌ Rejected | Race condition: device moves to 100% first, then automation corrects to 50%. Users see blind overshoot. Z-Wave queue pollution. |
| Script wrappers (update all callers) | ❌ Rejected | Misses Alexa, dashboard, future automations. Whack-a-mole maintenance burden. |
| **Template Covers** | ✅ **Chosen** | Clean command intercept before anything reaches the device. Covers all callers. Zero script changes. Globally configurable stop point. |

**How it works:**

```
caller (script / Alexa / Lovelace / any automation)
    ↓  cover.open_cover  →  cover.window_blind_controller_4
template cover  (cover.window_blind_controller_4)
    ↓  translates to:  cover.set_cover_position  position=50
physical hw entity  (cover.window_blind_controller_4_hw)
    ↓  Z-Wave  SET_VALUE
iBlinds v2 hardware  →  stops at 50%
```

`close_cover` and `set_cover_position` pass through unchanged — only `open_cover` is intercepted.

A single `input_number.iblinds_v2_open_position` (default 50%) controls the stop point across all v2 entities. It is adjustable via HA UI.

### Phase 3: Blueprint Deletion

The broken `iblinds_device_handler.yaml` blueprint was **deleted**. It had zero automation instances referencing it (confirmed in both YAML config and `.storage/`). Leaving dead, misleading code in the repository is a higher cost than deletion.

---

## Migration Steps for jshessen

### Step 1: Restart zwave-js-ui (if not already done)

```bash
docker restart zwave-js-ui
```

### Step 2: Re-interview v2 nodes in Z-Wave JS UI

Go to `http://<host>:8091` → each node below → **Node Actions → Re-interview node**:

- Node 67 (unknown — may need re-inclusion)
- Node 71 (Right Blinds: `cover.window_blind_controller`)
- Node 72 (Left Blinds: `cover.window_blind_controller_3`)
- Node 103 (Bedroom Blinds: `cover.window_blind_controller_4`)
- Node 106 (unknown — may need re-inclusion)
- Node 107 (Guest Blinds: `cover.window_blind_controller_2`)

After re-interview, each node's Group 1 should list the hub controller node ID.

### Step 3: Rename v2 physical entities in HA UI

**Settings → Entities** — find each entity, click it, click the pencil icon, change Entity ID:

| Current Entity ID | Change To |
|-------------------|-----------|
| `cover.window_blind_controller` | `cover.window_blind_controller_hw` |
| `cover.window_blind_controller_2` | `cover.window_blind_controller_2_hw` |
| `cover.window_blind_controller_3` | `cover.window_blind_controller_3_hw` |
| `cover.window_blind_controller_4` | `cover.window_blind_controller_4_hw` |

> Note: The `packages/iblinds_v2_covers.yaml` file is already committed. Do the entity renames **before** restarting HA, otherwise the template covers will show as unavailable until the `_hw` entities exist.

### Step 4: Restart Home Assistant

```bash
docker restart home-assistant
```

### Step 5: Verify

In **Developer Tools → States**:
- `cover.window_blind_controller_4` should exist as a template cover (not the Z-Wave entity)
- `cover.window_blind_controller_4_hw` should be the Z-Wave entity

Functional tests:
- `cover.open_cover` on any v2 entity → blind stops at 50% (not 100%)
- `cover.close_cover` → blind goes to 0%
- `cover.set_cover_position` with position=75 → blind goes to 75%
- `start_active_day` script → still works (calls open on bedroom + guest)
- `good_night` / `secure_home` scripts → still work (call close on v2 entities)

### Step 6: Adjust stop point (optional)

**Settings → Helpers → iBlinds v2 Open Position** — drag slider to desired default (10–100%, step 5%).

### Step 7: Nodes 67 and 106 (deferred)

After Z-Wave re-interview, if these nodes gain cover entities:
1. Rename their entities to `*_hw` suffix
2. Uncomment the stub entries at the bottom of `packages/iblinds_v2_covers.yaml`
3. Fill in actual entity IDs
4. Restart HA

---

## Trade-offs Accepted

| Trade-off | Cost | Why Acceptable |
|-----------|------|----------------|
| Template covers add one HA state evaluation hop | ~1ms latency | Imperceptible for blind positioning |
| Entity rename is a UI step, not YAML | One-time manual step | Cannot be automated; HA entity registry is managed via UI or `.storage` (not recommended to edit directly) |
| Position feedback depends on Lifeline being set up (Phase 1) | If re-interview not done, `_hw` entities show unknown → template shows unavailable | Phase 1 prerequisite is clearly documented; unavailable is visibly correct, not silently wrong |
| Per-device stop points not implemented | All 4 entities share one stop point | Acceptable for 2-person household; easy to extend (add per-device `input_number` and reference it) |

---

## Files Changed

| File | Change |
|------|--------|
| `zwave/.config-db/devices/0x0287/ib2_0.json` | Added Lifeline, treatSetAsReport, Binary Switch removal (Linus) |
| `packages/iblinds_v2_covers.yaml` | Created — template covers + stop-point input_number (Phase 2) |
| `blueprints/automation/jshessen/iblinds_device_handler.yaml` | Deleted — dead code (never fired, unfixable) |
| `docs/iblinds/ADR-001-iblinds-v2-stop-point.md` | This file |

---

## UX Accessibility

**Date of reassessment:** 2026-07-20  
**Trigger:** jshessen feedback — stop-point configuration is not discoverable or editable without YAML expertise. The original blueprint approach was chosen precisely to avoid this; the template cover approach is correct but creates a UX gap.

### The Problem

The Template Cover + `input_number` architecture is technically correct but UX-inaccessible. A user who wants to change the bedroom blind's stop point must:
1. Know that Settings → Helpers exists
2. Know that `iblinds_v2_node103_open_position` means "Bedroom Blinds"
3. Find and drag the right slider

This is a YAML-adjacent experience even though no YAML is edited. The original blueprint intent was to let users configure per-device behavior from the HA UI wizard (like creating an automation from a template) — no YAML, device picker, number slider, done.

### Why Blueprint Intercept Still Doesn't Work

Investigated all HA 2024+ mechanisms:

- **`cover_command` trigger:** Does not exist. No pre-command trigger is available to blueprints.
- **`zwave_js_value_notification`:** Hub-receives-report direction, not hub-sends-command direction. Cannot intercept.
- **`state: opening` + correction:** Functions, but has two problems: (1) race condition — blind moves 2–6% before correction fires; (2) `set_cover_position` disambiguation — the automation can't distinguish `open_cover` from `set_cover_position(80)` and would incorrectly intercept explicit position commands above the stop point.
- **Script wrapper:** Changes calling convention; misses Alexa, dashboards, other automations.

**Conclusion:** Template Covers remain the only clean intercept mechanism. Blueprints cannot replicate this without accepting documented limitations.

### Chosen Approach: Template Covers + UX Layer

**Keep the Template Cover package.** Add the UX layer that makes the stop-point configuration feel native:

#### 1. Helper name improvements (YAML, `packages/iblinds_v2_covers.yaml`)

Rename `name:` fields to use room context (entity IDs unchanged — no downstream breakage):

| Entity ID | Old Name | New Name |
|-----------|----------|----------|
| `iblinds_v2_open_position` | "iBlinds v2 Open Position" | "iBlinds v2 — Default Open Position" |
| `iblinds_v2_node71_open_position` | "iBlinds v2 Node 71 Open Position (Right Blinds)" | "Right Blinds — Open Stop Point" |
| `iblinds_v2_node107_open_position` | "iBlinds v2 Node 107 Open Position (Guest Blinds)" | "Guest Blinds — Open Stop Point" |
| `iblinds_v2_node72_open_position` | "iBlinds v2 Node 72 Open Position (Left Blinds)" | "Left Blinds — Open Stop Point" |
| `iblinds_v2_node103_open_position` | "iBlinds v2 Node 103 Open Position (Bedroom Blinds)" | "Bedroom Blinds — Open Stop Point" |

#### 2. Lovelace co-location (`lovelace/iblinds.yaml`, new file)

Each blind gets a cover tile + stop-point slider directly below it in the same card stack. User sees the blind control and can adjust its stop point in one view — no Helper navigation required. This is the primary discoverability solution.

#### 3. Area assignment (one-time UI step, no YAML)

After helper rename: Settings → Entities → assign each `*_open_position` helper to its correct area. Helpers then appear alongside cover entities in area overviews.

#### 4. Community blueprint (`blueprints/automation/jshessen/iblinds_v2_stop_point.yaml`)

For users deploying on their own systems without the Template Cover package: a blueprint using `state: opening` + `set_cover_position` correction. Zero YAML to configure. Trade-offs documented in blueprint description:
- 2–6% overshoot possible when blind is near stop point at command time
- Will intercept `set_cover_position` calls above stop point (disambiguation limitation)
- Coexists harmlessly with Template Covers when both are deployed

### Trade-off Accepted

Device card co-location (stop-point slider appearing on the Z-Wave device page alongside the cover entity) is **not achievable** without a custom Python integration. Template entities and `input_number` helpers created in YAML have no `device_id` binding and cannot share a device page with the Z-Wave entity. The cost of a custom integration (Python HACS package, HA version compatibility burden, weeks of development) is disproportionate to a 4-blind deployment. Area grouping + Lovelace co-location achieves equivalent discoverability with hours of work.

---

---

## ADR-002 Amendment: v3 "Unknown" Position Diagnosis (2026-04-16)

**Authors:** Livingston (Diagnostics), Linus (Z-Wave)

### Root Cause

All iBlinds v3 entities showed persistent "Unknown" position state. Investigation revealed a three-layer chain:

1. **Z-Wave layer**: v3 uses **Window Covering CC (CC 106)** instead of Multilevel Switch CC (CC 38). The entity unique IDs follow the pattern `{node}-106-0-currentValue-23` (property 23 = Horizontal Slats Angle — this IS the blind position for iBlinds).

2. **State chain**: All named blinds (Patricia's, Stella's, Hadley's, Bay, North/West/South Sunroom) are **Cover Groups** (platform: `group`) created via Settings → Helpers. They aggregate the `_horizontal_slats_angle` Z-Wave entities. Unknown cascades upward: `_horizontal_slats_angle` Unknown → cover group Unknown.

3. **No state persistence**: HA's `core.restore_state` contains no cover entity states (ZWave JS entities are not in the restore state store). After every restart, all Window Covering CC entities start as Unknown until the device sends a report.

4. **Suspected cause**: Like v2 (which sends Multilevel Switch Set instead of Report on lifeline), v3 likely sends Window Covering **Set** commands instead of Window Covering **Reports** on the lifeline, so ZWave JS discards them as commands rather than updating the value cache.

### Fix Applied

**File:** `zwave/.config-db/devices/0x0287/iblindsv3.json` (gitignored — on disk only)

Added to `compat` section:
```json
"treatSetAsReport": ["Window Covering"]
```

This mirrors the v2 fix (`treatSetAsReport: ["Multilevel Switch"]`). When v3 sends a Window Covering Set on the lifeline after movement, ZWave JS now treats it as a Report and updates the position value.

**Required action:** `docker restart zwave-js-ui` — then command each v3 blind once. After the first movement, position should resolve from Unknown to actual value.

### Entity Map (v3 cover groups → member entities → ZWave nodes)

| Named Group | Member Entities | ZWave Nodes |
|-------------|----------------|-------------|
| North Sunroom Blinds | SR: Blinds 9, SR: Blinds 10 | 80, 79 |
| West Sunroom Blinds | SR: Blinds 4, SR: Blinds 8, Bay Blinds | 82, 81, (group) |
| South Sunroom Blinds | SR: Blinds 1, SR: Blinds 3, SR: Blinds 2 | 102, 87, 109 |
| Sunroom Blinds | All sunroom groups above | — |
| Patricia's Blinds | SR: Blinds 3, SR: Blinds 4 | 87, 82 |
| Stella's Blinds | SR: Blinds 8, SR: Blinds 9 | 81, 80 |
| Hadley's Blinds | SR: Blinds 10 | 79 |
| Bay Blinds | SR: Blinds 6, SR: Blinds 5, SR: Blinds 7 | 108, 113, 125 |

### Bluetooth Docker Fix (2026-04-16)

**Symptom:** `habluetooth.manager` error: "Missing NET_ADMIN/NET_RAW capabilities for Bluetooth management."

**Finding:** `docker-compose.yml` already had `cap_add: [NET_ADMIN, NET_RAW]`, but `/run/dbus` was mounted **read-only** (`:ro`). HA's Bluetooth adapter management requires write access to D-Bus.

**Fix applied:** `docker-compose.yml` — changed `/run/dbus:/run/dbus:ro` → `/run/dbus:/run/dbus:rw`.

**Required action:** `make restart` (or `docker compose up -d`) to recreate the HA container with the new dbus mount mode.

---

## Open Items

- [ ] Re-interview v2 nodes (jshessen — requires physical hub access, Z-Wave JS UI)
- [ ] Rename 4 v2 entities in HA UI (jshessen — Settings → Entities)
- [ ] Identify and handle Nodes 67 and 106 (may need re-inclusion)
- [ ] **Rename `input_number` helper `name:` fields** in `packages/iblinds_v2_covers.yaml` (Rusty)
- [ ] **Create `lovelace/iblinds.yaml`** — blinds dashboard with co-located sliders (Rusty)
- [ ] **Register iblinds dashboard** in `lovelace.yaml` or `configuration.yaml` (Rusty)
- [ ] **Create `blueprints/automation/jshessen/iblinds_v2_stop_point.yaml`** — community blueprint (Rusty)
- [ ] **Assign helpers to areas** in HA UI after above deploy (jshessen — Settings → Entities)
- [x] Add `treatSetAsReport: ["Window Covering"]` to iblindsv3.json (Linus — 2026-04-16)
- [x] Fix Bluetooth dbus mount in docker-compose.yml (2026-04-16)
