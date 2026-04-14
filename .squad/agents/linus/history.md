# Linus — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Integration Specialist
- **Joined:** 2026-04-14T17:06:50.077Z

## Learnings

<!-- Append learnings below -->

### 2026-04-14: Mode system UI layer update
- Lovelace mode_dashboard.yaml: 10x house_mode→presence_mode, 2x night_mode→time_of_day (select not boolean), Guest button→guest_mode toggle, added guest_mode + work_from_home_mode cards to Primary Mode entities list
- Alexa mode_controls.yaml: house_mode→presence_mode, night_mode→guest_mode, added work_from_home_mode; time_of_day NOT exposed to Alexa (managed by scripts)

### 2026-04-14: Mode system refactor completed
All UI layer files updated and config-check validated. Full context — including all decisions, naming rationale, and deferred items — in `decisions.md` (entries: "Mode system UI layer update", "Mode system refactor completed", "Script architecture refactor").
