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
