# Squad Decisions

## Active Decisions

### 2026-04-14: UI-configurable helper schema design
**By:** Danny (Lead)
**What:** Defined 18 input helpers across 6 logical groups for the mode/routine system. All timing trigger times, brightness levels, color temps, delays, and positional values are moved out of hardcoded YAML into HA UI-manageable helpers. Mode flags and enumerated states (covered in main plan) round out the full picture.

**Why:** User wants all timing/level values manageable via HA UI; no YAML edits needed for behavior tuning. input_datetime time-only helpers used as automation triggers via `at: "{{ states('input_datetime.foo') }}"` are re-evaluated daily by HA's scheduler — UI changes take effect at the next occurrence with no restart required.

**Trade-offs:**
- Template-based time triggers (`input_datetime`) add negligible overhead vs static time strings; benefit is household-managed schedules without YAML access
- `initial:` in YAML is first-boot only — HA stores and restores last state from `.storage/` on restart; changing `initial:` post-deploy has no effect. A future `script.reset_defaults` could programmatically restore factory values if needed.
- Single `wake_blinds_delay_min` covers all morning blinds phasing rather than per-room granularity; split only if users request different timing per zone (e.g., bedroom vs. kids room open at different delays)
- Kids wake values (`wake_kids_*`) co-located with adult wake namespace for simplicity; easy to lift into a dedicated Kids Mode group when school schedule awareness (deferred feature) is implemented
- `night_bedroom_lamp_color_temp` range is full 153–500 mireds (not clamped to 400–500 warm-only); allows experimentation at cost of user error choosing a cool-white night setting
- `work_bedroom_blinds_pct` as input_number rather than binary preserves the 51% ergonomic position as a tunable value — correct tradeoff given monitor glare sensitivity varies by user

**Helper groups:**
- Group 1 — Schedule (6 × input_datetime): `schedule_good_morning_early/weekday/weekend`, `schedule_work_time_weekday`, `schedule_good_night_weekday/weekend`
- Group 2 — Wake Kitchen (4 × input_number): `wake_brightness_weekday/weekend`, `wake_color_temp_weekday/weekend`
- Group 3 — Wake Timing (2 × input_number): `wake_blinds_delay_min`, `wake_kids_lights_delay_min`
- Group 4 — Wake Kids (3 × input_number): `wake_kids_brightness`, `wake_kids_color_temp`, `wake_kids_transition_sec`
- Group 5 — Night (2 × input_number): `night_bedroom_lamp_brightness`, `night_bedroom_lamp_color_temp`
- Group 6 — Work (1 × input_number): `work_bedroom_blinds_pct`

---

### 2026-04-14: Jinja2 variable resolution pattern
**By:** Basher (Template Dev)
**Status:** Proposed — pending squad review

**What:** A canonical three-level Jinja2 variable resolution pattern for all HA scripts that read from `input_number` or `input_datetime` helpers. Every configurable script variable MUST use this pattern so the codebase is consistent and maintainable.

**Pattern 1 — `input_number` integer (primary):**
```yaml
variable_name: >-
  {%- set _caller = variable_name | default(none) -%}
  {%- set _helper = states('input_number.helper_entity_id') -%}
  {%- if _caller is not none -%}
    {{ _caller | int }}
  {%- elif _helper not in ('unavailable', 'unknown') -%}
    {{ _helper | int }}
  {%- else -%}
    SAFE_DEFAULT
  {%- endif -%}
```

**Key mechanics:**
- `variable_name | default(none)` — returns `none` for Jinja2 Undefined; preserves `0` (falsy-safe)
- `is not none` — correct check (not truthiness); `| default()` only catches `Undefined`
- `| int` — casts `"80.0"` (states() return type) to `80`; coerces bad strings to `0`
- `not in ('unavailable', 'unknown')` — covers both HA bad states
- `>-` YAML block scalar for multi-line variable templates

**Pattern 3 — `input_datetime` at: triggers:** Use entity reference form (`at: input_datetime.foo`) — no Jinja2 fallback possible in `at:`.

---

### 2026-04-14: Canonical Jinja2 patterns (supplemental)
**By:** Basher (Template Dev)

**Filter order:** Always `| int(default)`, never `| int | default(X)`. `default()` only catches Jinja `Undefined`, not int conversion errors.

**`delay:` dict form:** Template in `minutes:` is valid in HA 2025+; evaluated at runtime.

**`target.entity_id`:** `"{{ my_list | join(', ') }}"` works; passing list variable directly is also valid and preferred.

**`action:` vs `service:`:** Use `action:` in new scripts (canonical since HA 2024.8+).

---

### 2026-04-14: TBD entity ID resolution
**By:** Livingston (Troubleshooter)

**Kitchen cabinet lights:** `light.kitchen_light_3` — user-named "Kitchen Light" — Z-Wave dimmer. No dedicated under-cabinet entity exists; scripts use this entity at low brightness (~10–15%) for pre-dawn nav lighting.

**Guest Desk Lamp:** `light.guest_outlet_3` — user-named "Guest Desk Lamp", icon: `mdi:desk-lamp`, platform: `switch_as_x` backed by `switch.in_wall_outlet_tr_500s`. Use this wrapper (not `switch.guest_desk_lamp`) in automations.

**Person entities:** `person.jeff` (Jeff) and `person.patricia` (Patricia) — full list; no others in registry.

**Other relevant lights resolved:**
- `light.bedroom_lamps` — area: `main_bedroom` (light group, bedside lamps)
- `light.bedroom_lamps_2` — area: `kid_s_bedroom`, user-named "Kid's Lamps"
- No `light.office_*` / `light.study_*` / `light.home_office_*` entities exist in current registry

---

---

### 2026-04-14: Routing table now authoritative
**By:** Danny (Lead / Architect)
**Status:** Decided

**Summary:** `.squad/routing.md` has been replaced with a complete, authoritative routing table covering all team members and all known work domains for this Home Assistant Docker deployment project.

**What changed:**
- Replaced all `{domain N}` placeholder rows with real domain → agent mappings.
- Expanded to cover: automations, scripts, lovelace, input helpers, Jinja2 templates, template sensors, device integrations (Z-Wave/Zigbee/MQTT), Docker/Makefile, debugging/diagnostics, architecture decisions, session logging, and GitHub issue/PR lifecycle.
- Added ambiguous-domain clarifications (packages route to Rusty or Basher depending on content; input helpers route to Rusty for structure, Basher for template-driven logic).
- Added issue routing rows for all `squad:{member}` labels.
- Added a Quick Reference table (agent → domain) for fast lookup.

**Trade-offs:**
- Specificity vs. flexibility: explicit assignments could feel rigid; the rules section preserves re-routing via label swap.
- Packages ambiguity retained intentionally — callers must inspect content before routing.

**The routing table is now the single source of truth.** All future routing decisions should update this file.

---

### 2026-04-14: Mode system refactor completed
**By:** Rusty
**What:** Renamed presence_mode (was house_mode), removed Guest option, added time_of_day select, added guest_mode + work_from_home_mode booleans, added 7 input_number wake helpers, created input_datetime.yaml with 6 schedule helpers. Removed good_night_manual automation. All automation triggers now use input_datetime entity references.
**Why:** Eliminate redundant mode helpers (night_mode, day_modes, location_mode), make timings UI-configurable

---

### 2026-04-14: Script architecture refactor
**By:** Basher
**What:** good_morning rewritten to pre-dawn only. secure_home extracted from good_night. Two new scripts: start_active_day (full wake with input_number-backed vars), start_work_day (WFH setup). good_night updated: covers expanded, security phase delegates to secure_home, night_mode→time_of_day.
**Why:** Separate concerns — pre-dawn navigation vs full wake. Make secure_home reusable. Remove inline security logic from good_night.

---

### 2026-04-14: Mode system UI layer update
**By:** Linus
**What:** Updated lovelace mode_dashboard and Alexa mode_controls to reflect mode refactor. presence_mode replaces house_mode everywhere. Guest mode is now a boolean toggle (not a house_mode option). time_of_day select added to lovelace. Work from home mode added to both dashboards and Alexa.
**Why:** Mode system refactor — house_mode renamed to presence_mode, night_mode replaced by time_of_day select, Guest extracted to separate boolean.

---

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
