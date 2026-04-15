# Danny — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Lead
- **Joined:** 2026-04-14T17:06:50.075Z

## Learnings

### 2026-04-14: Designed 20-helper UI schema (6 groups: schedule/wake-kitchen/wake-timing/wake-kids/night/work)

Defined full UI-configurable helper schema for the mode/routine system. 6 input_datetime (schedule triggers) + 12 input_number (light levels, delays, positions) = 18 configurable values, plus 2 mode flags (input_boolean) and 2 enumerated states (input_select) already in plan. All timing/level values moved out of hardcoded YAML — tunable via HA UI with no YAML edits or restarts required. Complete YAML blocks written for `input_datetime.yaml` and `input_number.yaml` inclusion. Decision filed: `decisions.md`.

### 2026-04-14: Populated routing table in `.squad/routing.md`

Replaced unfilled `{domain}` placeholder template with a complete authoritative routing table covering all 7 team members and all known work domains for this Home Assistant Docker project. Added domain disambiguation for ambiguous cases (packages, input helpers). Decision filed: `decisions/inbox/danny-routing-table-filled.md`.

### 2026-04-16: Reviewed battery_dashboard.yaml — REJECTED (2 bugs)

Reviewed `lovelace/battery_dashboard.yaml` written by the Squad coordinator. Found two bugs requiring fixes:

1. **YAML `>-` scalar breaks markdown tables.** Both markdown cards (View 1 summary, View 2 detail table) use `content: >-` which folds newlines between table rows into spaces. Empirically verified with PyYAML: `>-` on `| Col A | Col B |\n|---|---|\n| v1 | v2 |` produces a single space-joined string. Tables won't render. Fix: use `|-` (literal block scalar).

2. **`"*.+*"` glob pattern in auto-entities attribute exclude filter.** Intended to match "any entity with a battery_last_replaced value" but glob interprets `.+` as literal characters (dot-plus), not regex. ISO date strings from Battery Notes don't contain a literal `.+` sequence, so the filter fails silently. Fix: use `"*"` which matches any non-empty value.

Correct patterns confirmed: `sort(attribute='0')` on tuples works (Jinja2 `make_attrgetter` converts digit strings to int), `is_number` filter and `selectattr` test are valid HA Jinja2, `as_timestamp | timestamp_custom` chain is correct, `options:` key in auto-entities include filters correctly passes `multiple-entity-row` config. Dashboard registration in `configuration.yaml` as a separate YAML-mode sidebar dashboard is properly configured.

Key architectural learning: YAML block scalar choice (`>-` vs `|-` vs `|`) is a common silent-failure pattern in HA Lovelace markdown cards. Any card with markdown tables or pre-formatted output MUST use literal (`|`) scalars, never folded (`>`). Decision filed: `decisions/inbox/danny-battery-dashboard-review.md`.

### 2026-04-17: Re-reviewed battery_dashboard.yaml — REJECTED (same 2 bugs, refined fix #2)

Re-review of commit `2024949`. Both bugs from 2026-04-16 remain unfixed. Performed comprehensive checklist review covering Jinja2 correctness, Battery Notes v3.4.3 attribute names, auto-entities syntax, multiple-entity-row config, and HA YAML anti-patterns. All attribute names confirmed correct. All Jinja2 patterns (namespace, is_number, sort(attribute='0'), as_timestamp chain) confirmed valid. Only the same 2 bugs remain.

**Refined recommendation for Bug 2:** Changed fix from `"*"` to `"?*"`. Empirical testing revealed `fnmatch("", "*")` returns `True` — so `"*"` would incorrectly exclude entities with empty-string `battery_last_replaced` attribute. `"?*"` requires ≥1 character, correctly excluding only entities with actual date values. Always test glob patterns with `fnmatch` edge cases (empty string, None-as-string).

Decision updated: `decisions/inbox/danny-battery-dashboard-review.md`.

### 2026-07-20: iBlinds v2/v3 consistency analysis — RECOMMENDATION COMPLETE

Synthesized Linus's Z-Wave research and Livingston's diagnostic findings into a comprehensive implementation plan for the mixed iBlinds v2/v3 environment. Key architectural decisions:

**Root cause identified:** Missing `associations` section in `ib2_0.json` device config prevents Lifeline group setup, so v2 devices never send unsolicited position reports. This explains the "unknown" state in HA entities.

**Contradiction resolved:** Owner reported "unknown" positions while Livingston found `currentValue` tracking. Both are correct — Z-Wave JS tracks *commanded* positions optimistically, but HA entities require *confirmed* reports from devices. Without Lifeline, devices never report back.

**Recommended approach: Option C (Combination)**
1. **Device config fix:** Add Lifeline association + Binary Switch CC removal compat flag to `ib2_0.json`. HIGH confidence this fixes position reporting.
2. **Blueprint deployment:** Deploy existing `iblinds_device_handler.yaml` blueprint (currently unused with 0 automation instances). Intercepts `cover.open_cover` and redirects to configurable stop point (50% default).

**Why both are needed:**
- Device config fixes root cause (position reporting) but can't fix stop point (v2 firmware limitation — no Parameter 4)
- Blueprint fixes stop point but can't fix position reporting
- Combined: v2 behaves identically to v3 from user perspective

**Key trade-offs documented:**
- Re-interview required for all 6 v2 nodes (operational disruption ~10 minutes)
- Blueprint adds event interception overhead (minimal — filters by entity ID)
- Binary Switch CC removal copied from v3 config — defensive, not empirically required for v2
- Nodes 67 and 106 not in device registry — may require troubleshooting or re-inclusion

**Files to modify:**
1. `zwave/.config-db/devices/0x0287/ib2_0.json` — add associations + compat sections
2. `home-assistant/config/automations.yaml` — add blueprint-based automation

Decision filed: `decisions/inbox/danny-iblinds-v2-implementation-plan.md`

### 2026-07-20: iBlinds v2 — Template Cover architecture for firmware stop-point limitation

**Correction to prior decision:** My 2026-07-20 plan (above) recommended deploying the `iblinds_device_handler.yaml` blueprint. That was wrong — Livingston confirmed the blueprint has been dead since HA 2022.4 when `call_service` events were removed from the event bus. Never fired once. Revised decision after full team synthesis:

**Pattern: Template Covers as firmware-limitation workaround**

When Z-Wave hardware lacks a configurable behavior that exists in newer firmware (v3 has Parameter 4 "Default ON Value"; v2 does not), the correct HA-layer fix is a **Template Cover** package — not an automation, not a blueprint, not script wrappers.

Key insight: The state-change-correction automation approach (trigger on `opening` state, send `set_cover_position` to correct) has an inherent race condition. The physical device starts moving before the automation fires. Users see overshoot. Template Covers intercept at the command layer — the `_hw` entity never receives an `open_cover`; it receives `set_cover_position` directly.

**Architecture pattern (iBlinds v2):**
1. Rename physical Z-Wave entity to `*_hw` suffix in HA UI  
2. Create template cover with original entity ID  
3. Template intercepts `open_cover` → `set_cover_position` at configured stop point  
4. `close_cover` and `set_cover_position` pass through to `_hw` unchanged  
5. Global `input_number` helper controls stop point — UI adjustable, no YAML edits  
6. Result: all callers (scripts, Alexa, Lovelace, automations) see no change — zero migration cost  

**Blueprint deletion criteria:** A blueprint should be deleted (not archived) when:
- It has zero automation instances (confirmed via YAML + `.storage/`)  
- Its core mechanism is permanently broken (removed platform/event)  
- The replacement approach is well-documented in an ADR  
Dead code that looks functional is more dangerous than no code.

**Files:** `packages/iblinds_v2_covers.yaml`, `docs/iblinds/ADR-001-iblinds-v2-stop-point.md`  
Decision filed: `decisions/inbox/danny-iblinds-architecture.md`

