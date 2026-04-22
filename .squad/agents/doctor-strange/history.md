# Doctor Strange — History

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

### 2026-04-21: Full Templates Audit — templates/ directory orphaned

Ran full audit of all 10 files in `templates/` directory and package-level template sensors.

**Critical discovery: `template: !include_dir_merge_list templates/` is MISSING from configuration.yaml.**
All 10 template files are orphaned — not loaded on HA restart. Entities persist in entity registry and restore_state from prior loads, masking the breakage until next full restart. The `check_config` command passes because it only validates files that are included.

**Rule added:** After any config restructuring, always verify `grep "templates/" configuration.yaml` returns a match — not just config-check passing.

**Patterns confirmed working (all templates that ARE loaded):**
- `has_value()` as availability guard on switch/light templates — correct pattern
- `states('input_select.active_holiday')` in name/icon templates — safe, all have else/default fallback
- YAML anchors (`&anchor` / `*alias`) — correct scope (per-file) and semantics

**Unit inconsistency found:** `energy_costs.yaml` uses `unit_of_measurement: "$"` on 3 monetary sensors while `amwater_water_costs.yaml` and `spire_gas_costs.yaml` use `"USD"`. HA treats these as different units.

**Package templates (alexa_helpers, ios_companion):** Both use `!= 'unknown'` guard on input_datetime reads but miss `'unavailable'` case. Pattern should be `not in ('unknown', 'unavailable', 'none', '')`.

**Decisions to propagate:** CRITICAL-1 (missing include) blocks safe restart. MODERATE-1 (unit inconsistency) should be fixed before energy dashboard is configured. Both filed in decisions/inbox.

### 2026-04-15: |-  vs >- for markdown card content; fnmatch vs regex in auto-entities

**`|-` vs `>-` for Lovelace markdown cards:**
- `>-` is YAML "folded block scalar" — collapses newlines into spaces. Correct for multi-line Jinja2 variable templates where whitespace is irrelevant.
- `|-` is YAML "literal block scalar with chomp" — preserves newlines exactly. **Required** for markdown `content:` fields because markdown table rows must be on separate lines to render as tables. Using `>-` on a markdown card collapses the table into a single line of garbage.
- Rule: `>-` for Jinja2 expression blocks; `|-` for any `content:` block that contains rendered markdown.

**fnmatch glob vs regex in auto-entities attribute filters:**
- auto-entities `attributes:` filter values use **fnmatch glob syntax**, NOT regex.
- `*.+*` is a regex pattern (meaning: any chars, then one-or-more of `.`, then any chars) — meaningless in fnmatch, matches nothing.
- `?*` is the correct fnmatch idiom for "one or more characters" (i.e., any non-empty string).
- Use `?*` to match "attribute has any non-empty value set"; use `*` to match any value including empty.

---

### 2026-04-20: Full Jinja2 audit — key findings

Completed a codebase-wide template audit covering `templates/`, `packages/`, `automations/`, `lovelace/battery_dashboard.yaml`.

**Critical bugs found:**

1. **Namespace-less loop mutation** (`holiday_season_controller.yaml`): Memorial Day and Labor Day both use `{% set var = ... %}` inside a `for` loop. Jinja2 inner-scope assignments never escape the loop. The "last Monday" and "first Monday" computations are silently no-ops. Both holidays display wrong results (Memorial Day: always "No Holiday" May 18-23, always "Memorial Day" May 24-31; Labor Day: only Sep 1 ever triggers). Fix: `namespace()` pattern on both loops.

2. **elif ordering swallows Cinco de Mayo and Memorial Day** (`holiday_season_controller.yaml`): The `elif month >= 2 and month <= 5` Easter block is too broad. It catches April 28-30 (Cinco de Mayo) and all of May (Memorial Day) before those specific elif branches can be reached. Cinco de Mayo is unreachable; Memorial Day May range is unreachable. Fix: move specific-date elif blocks before the broad month range.

**Medium findings:**
- `ios_companion.yaml` / `alexa_helpers.yaml`: `{% set now = ... %}` shadows the `now()` built-in. Works in current code but will silently break if template is extended. Rename to `_now_ts`.
- Same files: guard is `!= 'unknown'` only; `'unavailable'` during startup would cause TypeError. Use `has_value()`.
- `energy_costs.yaml`, `spire_gas_costs.yaml`, `amwater_water_costs.yaml`: No `availability:` templates. Sensors show `$0.00` instead of `unavailable` when sources are unavailable.
- `mode_management.yaml`: Uses deprecated `service:` key, not `action:`.
- `seasonal_displays.yaml` / `seasonal_living_room.yaml`: `default_entity_id:` is not a recognized HA template switch key — silently ignored.

**What's solid:**
- `iblinds_v2_covers.yaml` — exemplary; no issues
- Battery dashboard fleet summary — correct namespace + filter pattern
- Easter Computus algorithm — correctly implemented
- Energy cost tiered rate math — correct
- Filter order discipline — zero `| int | default` antipatterns anywhere
- All template files use `action:` (violations only in automation files)

Full report: `.squad/decisions/inbox/basher-template-assessment-2026-04-20.md`

---

### 2026-04-21: seasonal_living_room.yaml cleanup + missing alias audit

Removed invalid `default_entity_id:` key from smart switch block in `seasonal_living_room.yaml`. Same pattern as `seasonal_displays.yaml` cleanup done this session.

**Alias completeness audit:** Smart switch name template supports 6 seasonal names (Pumpkin, Present, Bunny, Flag, Living Room Display). Only Pumpkin and Present had static alias switches. Added missing:
- `Bunny` (Easter) — `unique_id: seasonal_living_room_bunny`, `icon: mdi:rabbit`
- `Flag` (Independence Day) — `unique_id: seasonal_living_room_flag`, `icon: mdi:flag-variant`

**Rule:** When a seasonal smart switch has an N-case name template, there must be N-1 static alias switches (all named cases except the generic fallback "Living Room Display" / "Display" etc.). The generic fallback name is not a useful Alexa voice target.

**Config check:** Passed clean (no error output from check_config).

---

### 2026-04-14: YAML scalar choice in Lovelace markdown cards

**Bug pattern:** Using `>-` (folded scalar) in `content:` fields of `type: markdown` cards collapses all newlines into spaces. Markdown tables depend on literal newlines to render rows — a folded scalar turns the entire table into one unreadable line.

**Rule:** In Lovelace markdown card `content:` blocks, always use `|-` (literal block scalar, strip trailing newline). Reserve `>-` only for Jinja2 template variable definitions in `variables:` maps or `template:` sensor value_templates.

**Context:** `battery_dashboard.yaml` — both View 1 summary table and View 2 Battery Notes detail table were broken with `>-`.

---

### 2026-04-14: auto-entities glob vs regex filter values

**Bug pattern:** `battery_last_replaced: "*.+*"` was an attempt to match any non-empty string using regex syntax (`.+` = one or more chars). But auto-entities `filter:` uses **glob wildcards**, not regex. The string `"*.+*"` matches only attribute values that literally contain `.+` — ISO date strings like `2024-06-15T10:30:00+00:00` do NOT match `.+` literally.

**Fix:** Use `"*"` to match any value (including empty), or `"?*"` to match one-or-more characters. For "has any replacement date set", `"*"` is the correct choice per Nick Fury's spec.

**Rule:** Never use regex patterns in auto-entities filter attribute values. Glob only: `*` (any), `?` (single char), `[abc]` (char class).

---

## 2026-04-16: Battery Dashboard v6 Implementation

**Task:** Rewrite Monitor view using correct battery-state-card v4.2.0 API

**What Was Written:**
- Complete v6 rewrite of `/home-assistant/config/lovelace/battery_dashboard.yaml`
- Monitor view: 3 cards (fleet summary + full fleet by room + needs attention)
- Manage view: Unchanged from v5 (uses auto-entities, no battery-state-card bugs)

**Key Design Decisions:**

1. **`default_config_base: false` on all cards**
   - Prevents shallow-merge of unwanted defaults
   - Card must explicitly define all properties

2. **Fleet Summary (markdown)**
   - Jinja2 namespace loop over `*_battery_plus` sensors
   - Direct state counting: critical (<20%), low (20-39%), OK (≥40%)
   - Replaced v5's binary_sensor approach (wrong threshold logic)

3. **Full Fleet by Room (Card 2)**
   - `group: [{by: "device.area_name"}]` — dynamic area grouping
   - Uses device.area_name resolution (entities have area_id=None, device has area)
   - `sort: [{by: "state"}]` — replaces deprecated `sort_by_level`
   - secondary_info: `"{attributes.battery_type_and_quantity} · {attributes.battery_last_replaced|reltime()}"`
   - Note: Patricia's phone (no area) will appear ungrouped — acceptable

4. **Needs Attention (Card 3)**
   - `exclude: computed.state >= 40` removes OK devices BEFORE grouping
   - `group: [{max: 19}, {min: 20, max: 39}]` — correct bucket assignment
   - Garage Entry Lock (32%) now correctly appears in Low group (not Critical)
   - Replaced v5's invalid `collapse: [{from: 0, to: 19}]` syntax

5. **Colors**
   - HA CSS variables: `var(--label-badge-red/yellow/green)`
   - Thresholds: 20%, 39%, 100%

6. **bulk_rename**
   - Strips " Battery+" suffix added by Battery Notes
   - Pattern: `{from: " Battery+", to: ""}`

**Caveats:**

1. **reltime() parsing** — `battery_last_replaced|reltime()` converts ISO dates to relative time ("3 months ago"). If Date.parse() fails, it renders raw attribute (graceful degradation). Post-deploy verification needed.

2. **Area grouping fallback** — If `device.area_name` doesn't resolve in `by:` property, fallback to explicit per-area filter groups is available (entity→area map documented in plan).

3. **Frontend-only validation** — Config check will warn about custom integrations (battery-state-card, auto-entities), but HA can't validate frontend-only cards. Browser console monitoring required post-deploy.

**Validation:**
- ✅ Config check passed: `docker exec home-assistant python -m homeassistant --script check_config -c /config`
- No errors related to YAML structure
- Custom card warnings expected and ignorable

**Files Modified:**
- `/home-assistant/config/lovelace/battery_dashboard.yaml` — full rewrite

**Status:** Ready for testing. Requires HA restart and visual verification:
- Fleet summary counts match actual device count
- Room groups appear correctly
- Garage Entry Lock shows in Low group
- reltime() renders as relative string (not raw ISO)

### 2026-04-16: Battery Dashboard v6 — Implementation Complete

Implemented complete Monitor view rewrite with correct battery-state-card v4.2.0 API patterns. All v5 bugs fixed:

**Design Decisions:**

1. **Fleet Summary (Markdown):** Jinja2 namespace loop over *_battery_plus sensors (not binary_sensor) with direct state bucketing (critical <20%, low 20-39%, OK ≥40%). Replaced v5's incorrect binary sensor threshold logic.

2. **Full Fleet by Room:** Dynamic `group: [{by: "device.area_name"}]` with explicit per-area fallback groups. `sort: [{by: "state"}]` sorts low→high. `secondary_info` displays battery type + reltime() for replacement date.

3. **Needs Attention:** `exclude: computed.state >= 40` removes OK devices (dynamic, real-time filtering). `group: [{max: 19}, {min: 20, max: 39}]` corrects bucket assignment. Garage Entry Lock (32%) now appears in Low group (not Critical).

4. **Config:** `default_config_base: false` on all cards disables shallow-merge collisions. Verbose YAML but eliminates hidden interactions.

5. **Styling:** HA CSS variables (red/yellow/green) with thresholds 20%/39%/100%. `bulk_rename` strips " Battery+" suffix.

**Validation:**
- ✅ Config check passed
- ✅ YAML structure verified
- ⏳ Post-deploy visual verification needed (reltime() rendering, area grouping, Garage Entry Lock placement)

**Key Learning:** YAML block scalars matter in HA Lovelace. `>-` (folded) collapses markdown tables into garbage; `|-` (literal) required for `content:` blocks. For Jinja2 templates, `>-` is correct. Choose based on output type, not preference.

**Caveat — reltime() Parsing:** If Date.parse() fails on `battery_last_replaced` ISO strings, card gracefully degrades to raw attribute. Visual verification required post-deploy. Fallback: remove `|reltime()` if raw ISO strings appear instead of relative time.

Manage view unchanged (uses auto-entities, no battery-state-card bugs). Dashboard ready for HA restart.

---

### 2026-04-21: seasonal_displays.yaml — Completion

**State when found:** Incomplete. File was mid-edit in a prior session.

**Issues fixed:**
1. `default_entity_id:` removed from SMART SWITCH — not a valid HA template switch key (silently ignored).
2. Added two missing static aliases:
   - "Shamrock Display" (`unique_id: seasonal_shamrock_display`, icon `mdi:clover`) — St. Patrick's Day
   - "Patriotic Display" (`unique_id: seasonal_patriotic_display`, icon `mdi:flag-variant`) — Independence Day
3. Updated header comment to list all 6 aliases.

**Evidence of incompleteness:** SMART switch name template referenced 6 holiday names (incl. Shamrock Display and Patriotic Display) but header and static alias section listed only 4. Pattern from `seasonal_living_room.yaml` confirms aliases should exist for every name the SMART switch can surface.

**Physical entity referenced:** `switch.plug_in_front_yard_adapters` — used for state, availability, turn_on, turn_off. Existence unverified (flag for Hawkeye/Iron Man).

**Config check:** Passed (exit 0).

**Note re: seasonal_living_room.yaml:** Same file also has `default_entity_id:` — same invalid key. Not fixed in this session (out of scope), but should be cleaned up.

**Pattern locked in:** Static alias count must match SMART switch name variant count. Every holiday name surfaced by the SMART switch should have a year-round Alexa alias.
