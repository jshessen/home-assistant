# Basher — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Template Dev
- **Joined:** 2026-04-14T17:06:50.077Z

## Learnings

### 2026-04-14: Canonical Jinja2 variable resolution pattern

Designed the three-level fallback idiom for all `input_number`-backed script variables. Pattern is:

```
_caller = variable | default(none)  →  input_number state  →  hardcoded default
```

Key mechanics locked in:
- `| default(none)` catches Jinja2 `Undefined` (caller didn't pass the field); keeps `0` intact (falsy-safe)
- `is not none` check (not a truthiness check) to decide if caller override is present
- `not in ('unavailable', 'unknown')` guards the helper state read
- `| int` casts `"80.0"` (what `states()` returns for float-stored `input_number`) to `80`
- `>-` YAML block scalar for multi-line variable templates
- `input_datetime` in automation `at:` uses entity reference form directly — no Jinja2 fallback possible there

### 2026-04-14: Defined canonical three-level Jinja2 resolution pattern: caller | default(none) → states() guard → hardcoded default. `>-` scalar, | int cast.

### 2026-04-14: Mode system script refactor

- good_morning rewritten to pre-dawn only (kitchen nav light at 20%, color_temp 425); no blinds or delays
- good_morning_weekday/weekend stubs removed from good_morning.yaml entirely
- secure_home.yaml created at SCRIPTS DIR — delegates lock+garage+covers from good_night
- good_night.yaml: security phase replaced with script.secure_home call, night_covers expanded to include bedroom+kids, guest_covers added, night_mode→time_of_day, is_guest_mode now checks input_boolean.guest_mode
- start_active_day.yaml created — full wake routine with input_number-backed variables; time_of_day=Day set at END
- start_work_day.yaml created — fan off, bedroom blinds partial, desk lamp on, work_from_home_mode=on
- Variable resolution 3-level pattern: caller(is not none) → helper state → default; always cast states() return

Full pattern suite locked in for all `input_number`-backed script variables. Three levels: caller override (`variable | default(none)` + `is not none` check) → live helper state (`states()` + `not in ('unavailable', 'unknown')` guard + `| int` cast) → hardcoded safe default. `>-` YAML block scalar required for multi-line variable templates. `input_datetime` at-triggers use entity reference form directly \u2014 no Jinja2 fallback possible. Supplemental: `| int(default)` filter order, `action:` over `service:`, delay dict template form, list join in `target.entity_id`. Applied to `start_active_day.yaml` (Phase 1 Step 3) and all future configurable scripts. Decision filed: `decisions.md`.
### 2026-04-14: Mode system refactor completed
All script files updated and config-check validated. Full context — including all decisions, trade-offs, and entity ID resolutions — in `decisions.md` (entries: "Script architecture refactor", "Mode system refactor completed", "Canonical Jinja2 patterns", "TBD entity ID resolution").

### 2026-04-15: HA 2026.4 Template Function Audit
Audited entire deployment for opportunities to use new HA 2026.4 template functions:
- `entity_name(entity_id)` — replaces `state_attr(entity, 'friendly_name')`
- `state_attr_translated(entity, attr)` — human-readable HVAC mode translations

**Audit scope:** 32 YAML files across `templates/`, `packages/`, `scripts/`, `automations/`

**Result:** **Zero instances requiring conversion.** Key findings:
- No legacy `state_attr(entity, 'friendly_name')` calls found in scope
- One use of `map(attribute='name')` in battery_monitoring.yaml — this is the IDIOMATIC pattern for pipelines, NOT a candidate for entity_name()
- No HVAC/climate entities in deployment — no opportunity for `state_attr_translated()`
- Seasonal icon maps are custom business logic, not HA state translations

**Critical insight:** `entity_name()` is for isolated entity_id → name lookups, NOT for selectattr/map pipelines. The existing `map(attribute='name')` pattern is semantically clearer and chain-friendly.

**Out of scope:** Blueprint `iblinds_device_handler.yaml` contains 7 legacy friendly_name calls, but blueprints weren't in audit scope and need backward compatibility evaluation.

**Function availability confirmed:** Both functions exist in HA 2026.4.2 as template functions AND Jinja2 filters:
```python
entity_name(hass, entity_id) -> str | None
# Exposed as: entity_name('sun.sun') or 'sun.sun' | entity_name
```

Deployment uses modern, idiomatic HA patterns — no changes required. Full report: `.squad/decisions/inbox/basher-template-audit-2026-04-15.md`