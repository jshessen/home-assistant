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
