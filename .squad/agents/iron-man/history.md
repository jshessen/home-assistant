# Iron Man — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Automation Engineer
- **Joined:** 2026-04-14T17:06:50.076Z

## Learnings

<!-- Append learnings below -->

### 2026-04-20: Full Automation/Script/Lovelace/Helper Audit
- **Critical: `input_button.good_night_mode`** — Referenced in `automations.yaml` id `1752004821602` but no YAML definition exists anywhere. Likely a UI-only helper (hidden from VCS). Must be declared in `packages/mode_helpers.yaml` or documented.
- **Critical: `battery_monitoring.yaml` broken** — Jinja2 `zip()` is not available in HA templates (Python builtin only). The notification message template will error at runtime. File is also redundant with `battery_notes.yaml` event-driven approach — recommend deprecating it.
- **Critical: `mode_management.yaml` uses `service:` everywhere** — 8 occurrences. Needs bulk conversion to `action:`.
- **Critical: `all_persons_away` has no `for:` guard** — GPS blip will trigger `secure_home` with occupants inside. Add `for: minutes: 3` on triggers.
- **`good_morning_early` lacks presence guard** — Kitchen light turns on even in Away/Vacation mode.
- **Good Night script hardcodes holiday switches** — New holiday devices added via label won't be turned off at night.
- **~50+ `service:` calls across scripts and packages** — Mechanical but important cleanup debt.
- **~11 `platform:` trigger calls** — Old syntax, should be `trigger:` key.
- **Missing automations:** (1) Return home presence update, (2) Evening time_of_day transition, (3) Garage failure notification.
- **Holiday season controller** — Memorial Day loop logic is fragile (no break in Jinja2, relies on iteration order).
- **Battery dashboard** — Excellent design, fleet summary + hold-to-replace UX.
- **`secure_home.yaml`** — Good design: parallel lock+garage with wait_template and continue_on_timeout.
- **`start_active_day.yaml`** — Input-number variable fallback chain is best-practice pattern for UI-configurable scripts.
- battery-state-card refactor pattern: filter on `*_battery_plus`, `bulk_rename` strips " Battery+" suffix → clean display names, `secondary_info` shows type+days as `{attributes.battery_type_and_quantity} · {attributes.battery_last_replaced_days}d`, `collapse` with `default_hide: true` folds Good tier (≥40%) so page stays scannable; binary_sensor and "never replaced" rows still need auto-entities as battery-state-card only handles numeric sensors
- Mode system renamed: house_mode→presence_mode, night_mode→time_of_day (input_select), guest_mode (boolean), work_from_home_mode (boolean)
- New input_datetime.yaml at CONFIG ROOT — add `input_datetime: !include input_datetime.yaml` to configuration.yaml
- Automation triggers now use `at: input_datetime.schedule_NAME` entity form (not hardcoded times)
- good_night_manual automation removed (feedback loop risk)
- New automations: good_morning_early (5:30am daily), work_time_weekday, all_persons_away (stub)

### 2026-04-14: Mode system refactor completed
All files updated and config-check validated. Full context — including all decisions, trade-offs, and entity ID resolutions — in `decisions.md` (entries: "Mode system refactor completed", "Script architecture refactor", "Mode system UI layer update", "TBD entity ID resolution", "UI-configurable helper schema design").

### 2026-04-15: Purpose-Specific Triggers Investigation
- **Finding:** "Purpose-Specific Triggers" mentioned in Vision's briefing **does not exist** in HA 2026.4.2
- **Labs System:** Confirmed HA has Labs feature system (Settings → System → Labs), UI-only configuration
- **Current Labs:** Only `analytics/snapshots` preview enabled; no semantic trigger features available
- **Trigger Types:** HA 2026.4.2 has: state, numeric_state, time, time_pattern, event, homeassistant triggers
- **Closest Equivalent:** Labels (cross-domain grouping), template sensors (semantic states), device_class (auto-discovery)
- **Automation Opportunities Identified:**
  1. Battery monitoring with device_class auto-discovery (HIGH VALUE - single template sensor replaces manual entity lists)
  2. Label-based motion detection (deferred - current 2-person deployment too simple)
  3. Door/window security templates (future - need sensors first)
- **Documentation:** Created `docs/setup/labs-features.md` with full research findings and modern trigger pattern examples
- **Decision Inbox:** Filed `.squad/decisions/inbox/rusty-purpose-specific-triggers.md` with battery monitoring implementation proposal
- **Key Insight:** Modern HA patterns (labels + templates + device_class) achieve semantic trigger goals without new features

### 2026-04-15: Battery Monitoring Automation Implementation
- **Implementation:** Created `automations/battery_monitoring.yaml` - self-maintaining battery level monitor
- **Trigger Pattern:** Dual trigger approach:
  1. Daily time trigger at 09:00:00 for routine check
  2. Template trigger with `value_template` watching ALL battery sensors via device_class filter - fires when any battery crosses below 20%
- **Auto-Discovery:** Uses `states.sensor | selectattr('attributes.device_class', 'eq', 'battery')` pattern - no hardcoded entity list required
- **Notification:** Sends alerts to both `notify.mobile_app_jeff` and `notify.mobile_app_patricia` with formatted list of device names and current battery levels
- **Condition Guard:** Template condition ensures notification only fires when low batteries actually exist (prevents empty alerts)
- **Message Template:** Uses Jinja2 `zip()` function to pair device names with battery levels for clean bullet-list output
- **Maintenance Benefit:** Zero-touch when adding new battery-powered devices - automation discovers them automatically via device_class attribute
- **Config Validation:** Passed HA config check before commit
- **Commit:** `08d391c` - feat(automations): Add battery monitoring automation

### 2026-04-15: Evening AI Summary Automation with Structured Output
- **Implementation:** Created `automations/evening_ai_summary.yaml` from Vision's design specification
- **New Pattern:** Uses `ai_task.generate_data` with `structure` parameter (HA 2026.x feature) for typed LLM output
- **Key Advantage:** Structured output returns typed fields accessible via `response_variable.data.field_name` - eliminates free-text parsing brittleness
- **Structure Definition:** 3 string fields: `summary` (2-sentence home status), `security_note` (lock status), `tomorrow_note` (mode-based future context)
- **LLM Integration:** Uses Ollama (llama3.2:3b) via "Ollama Control" integration at localhost:11434
- **Context Inputs:** Person states (jeff/patricia), presence_mode, time_of_day, guest_mode, work_from_home_mode, weather, 3 lock entities
- **Trigger:** Time trigger at 21:00:00 with condition requiring `input_select.presence_mode = Home`
- **Notifications:** Dual delivery to `notify.mobile_app_jeff` and `notify.mobile_app_patricia` with structured emoji-prefixed sections
- **Benefits Over Traditional:** No markdown/JSON parsing needed, deterministic automation logic, LLM output constrained to requested schema
- **Schema Design:** Kept flat (3 string fields) for optimal LLM reliability - Vision recommends 3-5 fields max
- **Config Validation:** Passed HA config check before commit
- **Commit:** `9c53749` - feat: Add evening AI summary automation with structured output

### 2026-07-20: iBlinds v2 Stop-Point Automation Design

- **Problem:** iBlinds v2 (fw 1.65) lacks Parameter 4 (Default ON Value), which v3 uses natively for stop-point on open. v2 `open_cover` always goes to 100%.
- **Blueprint is dead:** The existing blueprint (`iblinds_device_handler.yaml`) uses `call_service` events that were removed from HA's event bus in 2022.4. It has never fired, ever. Cannot be fixed — architecture is incompatible with modern HA.
- **Nick Fury's plan B1 (blueprint) is wrong:** Nick Fury's implementation plan recommends deploying the blueprint for Phase 2. That won't work. Replaced with Template Covers approach.
- **Chosen pattern: Template Cover Package** (`packages/iblinds_v2_covers.yaml`)
  - Physical Z-Wave entities renamed to `*_hw` suffix in entity registry (UI step)
  - Template covers take original entity IDs — all existing scripts work unchanged
  - `cover.open_cover` → intercepted by template → `cover.set_cover_position` at stop point
  - `cover.close_cover` → passes through to physical entity unchanged
  - `cover.set_cover_position` → passes through to physical entity unchanged
  - Global `input_number.iblinds_v2_open_position` (default 50%) for configurable stop point
- **Entity ID map:**
  - Node 71 (Right): `cover.window_blind_controller` → `cover.window_blind_controller_hw`
  - Node 72 (Left): `cover.window_blind_controller_3` → `cover.window_blind_controller_3_hw`
  - Node 103 (Bedroom): `cover.window_blind_controller_4` → `cover.window_blind_controller_4_hw`
  - Node 107 (Guest): `cover.window_blind_controller_2` → `cover.window_blind_controller_2_hw`
  - Nodes 67, 106: TBD — need Z-Wave re-interview first
- **Key constraint:** HA template covers require `name:` to exactly match the original friendly name so slugified entity_id is identical (e.g., "Window Blind Controller 4" → `cover.window_blind_controller_4`)
- Per-device `input_number` with 0-sentinel fallback pattern: use `min: 0, initial: 0` and resolve in Jinja as `{% set per = states('input_number.device_specific') | int(0) %}{{ per if per > 0 else states('input_number.global') | int(default) }}`. Value 0 acts as sentinel meaning "inherit from global." This avoids duplicate state and keeps a single source of truth while allowing per-device overrides.
- iblinds dashboard layout fix: room sections (markdown header + content cards) must be wrapped in a single `type: vertical-stack` to prevent masonry layout scatter. Without wrapping, HA's masonry engine treats the header and content as independent grid items and can place them in different columns. All 11 room sections across v2 and v3 views were fixed with this pattern.

### 2026-07-20: Battery Dashboard v4 — 2-Tab Redesign

- **Collapse bug root cause:** battery-state-card with only ONE `collapse` group defined causes ALL items to land in that group regardless of actual level. Fix: define all tiers exhaustively (Critical 0-19, Low 20-39, Good 40-100) so the card can bucket correctly.
- **Jinja2 operator precedence:** `sensors | count - low | count` is wrong — `|` is high precedence so this computes `sensors | (count - low) | count`. Always use explicit parens: `(sensors | count) - (low | count)`.
- **Battery Notes threshold trap:** `exclude: attributes.battery_low: false` only shows devices Battery Notes itself considers low (below their configured threshold). A device at 32% with a 10% threshold = NOT flagged. For "visually concerning" devices, filter on `state < 40` instead of the `battery_low` attribute.
- **4→2 tabs:** Overview + All Devices + Maintenance + Details collapsed to Status + Manage. battery-state-card's collapse feature replaces the need for separate "overview" and "all devices" tabs — 3-tier collapse handles both roles in one card.
- **Never write to decisions/inbox without also appending to history.md** — the two are always paired.

### 2026-04-21: Automation & Script Audit
- **`service:` is GONE from all hand-crafted automations/ and core scripts/** — bulk cleanup from prior sessions worked. Only remaining `service:` is in 5 keymaster alias scripts + 1 master script + 1 UI automation in automations.yaml.
- **`input_button.good_night_mode` RESOLVED** — was missing in prior audit; now properly defined in `input_button.yaml`. The UI automation referencing it is structurally correct.
- **`platform:` (old trigger syntax) remains in 3 automation files** — `battery_monitoring.yaml` (2), `evening_ai_summary.yaml` (1). Also in 8 package automations (ios_companion, alexa_helpers, spire, amwater, ameren, rtl433). All functional, deprecated only.
- **Duplicate battery monitoring** — `battery_monitoring.yaml` and `battery_notes.yaml` both send low-battery notifications. Decision needed: deprecate `battery_monitoring.yaml` in favor of Battery Notes events?
- **`good_morning_early` still lacks presence guard** — flagged in 2026-04-20 audit, not yet fixed. Kitchen light turns on in Away/Vacation mode.
- **Good Night hardcoded holiday switches** — still hardcoded to 4 switch names. Label-based approach would auto-expand. Defer until Hawkeye confirms label entity coverage.
- **Keymaster scripts** — 5 alias scripts and 1 master all use `service:`. Placeholder comment `# Replace with your actual entity` is stale but entity IDs are correct. Low risk but creates noise.
- **Holiday system is well-designed** — single source of truth in `holiday_season_controller.yaml`, label-based targeting in decorations, no duplicate date logic.
- **Core scripts (good_night, good_morning, secure_home, start_active_day, start_work_day)** — all clean, `action:` syntax throughout, variable-driven entity lists, good guard patterns.
