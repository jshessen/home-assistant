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
