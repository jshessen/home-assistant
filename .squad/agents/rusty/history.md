# Rusty — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Automation Engineer
- **Joined:** 2026-04-14T17:06:50.076Z

## Learnings

<!-- Append learnings below -->
- Mode system renamed: house_mode→presence_mode, night_mode→time_of_day (input_select), guest_mode (boolean), work_from_home_mode (boolean)
- New input_datetime.yaml at CONFIG ROOT — add `input_datetime: !include input_datetime.yaml` to configuration.yaml
- Automation triggers now use `at: input_datetime.schedule_NAME` entity form (not hardcoded times)
- good_night_manual automation removed (feedback loop risk)
- New automations: good_morning_early (5:30am daily), work_time_weekday, all_persons_away (stub)

### 2026-04-14: Mode system refactor completed
All files updated and config-check validated. Full context — including all decisions, trade-offs, and entity ID resolutions — in `decisions.md` (entries: "Mode system refactor completed", "Script architecture refactor", "Mode system UI layer update", "TBD entity ID resolution", "UI-configurable helper schema design").

### 2026-04-15: Purpose-Specific Triggers Investigation
- **Finding:** "Purpose-Specific Triggers" mentioned in Yen's briefing **does not exist** in HA 2026.4.2
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
