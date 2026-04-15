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

## Open Items

- [ ] Re-interview v2 nodes (jshessen — requires physical hub access, Z-Wave JS UI)
- [ ] Rename 4 v2 entities in HA UI (jshessen — Settings → Entities)
- [ ] Identify and handle Nodes 67 and 106 (may need re-inclusion)
- [ ] Optional: Add Lovelace slider for `iblinds_v2_open_position` to mode dashboard
- [ ] Optional: Per-device stop points if bedroom/living-room need different values
