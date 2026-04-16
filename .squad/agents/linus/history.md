# Linus — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Integration Specialist
- **Joined:** 2026-04-14T17:06:50.077Z

## Learnings

<!-- Append learnings below -->

### 2026-04-15: battery-state-card v4.2.0 full feature audit

**Latest version:** v4.2.0 (released 2026-04-02). Our dashboard uses the card but with several deprecated/legacy properties.

**Key deprecated items in current dashboard:**
- `sort_by_level: true` — deprecated since v3.0.0; correct form is `sort: "state"` (or `sort: [{by: "state"}]`)
- `from`/`to` in collapse groups — docs specify `min`/`max` for Group objects; `from`/`to` may be legacy aliases that still work but are undocumented
- `filter.exclude` on raw `state` — v4.1.0 recommends `computed.state` for post-transformation filtering

**Major features we're NOT using:**
1. **Dynamic grouping (`by` property)** — `by: "area.name"` or `by: "attributes.battery_type"` auto-creates groups, no manual definition needed
2. **Group keywords** — `{count}`, `{min}`, `{max}`, `{avg}`, `{range}` in group `name`/`secondary_info`
3. **Composite filters** (`and`/`or`/`not`) — fine-grained entity inclusion/exclusion logic
4. **`tap_action` with KString** — tap row → navigate to device page, call service, trigger replacement script. `navigation_path: "/config/devices/device/{attributes.device_id}"` works.
5. **`reltime()` KString function** — `"{last_changed|reltime()}"` shows "3 days ago" instead of ISO timestamp
6. **`charging_state`** — detect and indicate charging from entity state or attribute
7. **Gradient colors with `colors.steps`** — explicit gradient instead of implicit defaults; `steps: ['#ff0000','#ffff00','#00ff00'], gradient: true`
8. **`device.labels` filtering** — tag devices in HA and filter by label (`operator: contains, value: "my_label"`)
9. **`secondary_info` with piped functions** — e.g. `"{attributes.battery_type_and_quantity} · changed {last_changed|reltime()}"`
10. **`battery_notes_dedup`** — enabled by default; de-dupes battery_plus vs raw battery entities
11. **`default_config_base: false`** — needed when managing entities externally (e.g. auto-entities)
12. **`style`** — inject custom CSS into shadow DOM per-entity or card-level
13. **`value_override`** — override displayed battery level via KString
14. **`debug`** — per-entity or global; shows full entity data object in card for troubleshooting
15. **`unpack`** — unpack sensor group `entity_id` arrays into individual batteries

**Filter fields available:**
- `entity_id`, `state`, `computed.state`, `attributes.*`, `entity.*`, `device.*`, `area.*`, `device.labels`
- Operators: `=`, `>`, `>=`, `<`, `<=`, `contains`, `matches` (wildcard `*` or regex `/pattern/`), `exists`, `not_exists`
- Dynamic value references: `{input_number.threshold}` in filter `value` field
- Composite: `and`, `or`, `not` wrappers

**Sort options:**
- By: `"state"` or `"name"` (display values) or `entity.*` raw paths e.g. `entity.last_changed`, `entity.attributes.battery_level`
- `desc: true` for descending
- Multi-level: list of sort objects

**Limitations confirmed:**
- Include filters processed once at page load (no dynamic include by changing state)
- No integration-based discovery natively (no `integration_entities()`)
- Gradient colors require hex colors only
- Can't put a standalone button inside a row (whole row is the tap target)
- No Jinja2 templating in config values (KString is the only dynamic system)

**Full decision doc:** `.squad/decisions/inbox/linus-battery-state-card-features.md`

### 2026-04-14: Mode system UI layer update
- Lovelace mode_dashboard.yaml: 10x house_mode→presence_mode, 2x night_mode→time_of_day (select not boolean), Guest button→guest_mode toggle, added guest_mode + work_from_home_mode cards to Primary Mode entities list
- Alexa mode_controls.yaml: house_mode→presence_mode, night_mode→guest_mode, added work_from_home_mode; time_of_day NOT exposed to Alexa (managed by scripts)

### 2026-04-14: Mode system refactor completed
All UI layer files updated and config-check validated. Full context — including all decisions, naming rationale, and deferred items — in `decisions.md` (entries: "Mode system UI layer update", "Mode system refactor completed", "Script architecture refactor").

### 2026-04-15: Ollama local LLM deployment
- Created `docker-compose.ollama.yml` with Ollama service using `llama3.2:3b` model
- Container name: `ollama`, port 11434, volume: `./ollama/models` → `/root/.ollama`
- Network: home-automation bridge (172.16.2.0/27) with exposed port for HA host-network access
- Updated Makefile: added `COMPOSE_OLLAMA`/`OLLAMA_SERVICE` variables, `ollama` target (HA + Ollama), added to `all` target
- Created setup guide at `home-assistant/config/docs/setup/ollama-setup.md` covering:
  - Start command: `make ollama`
  - First-run model pull: `docker exec ollama ollama pull llama3.2:3b`
  - Dual-config pattern: Two HA integration entries ("Ollama Chat" for conversation, "Ollama Control" for device actions)
  - Assist pipeline wiring: Settings → Voice Assistants → set Conversation Agent to "Ollama Chat"
  - Troubleshooting and maintenance procedures
- Verified port 11434 availability before deployment
- Updated `docs/README.md` to include Ollama setup guide reference

### 2026-04-15: iBlinds v2 Z-Wave position reporting research
**Problem:** v2 units (fw 1.65, nodes 67/71/72/103/106/107) show "unknown" position at all times; v3 units work correctly.

**Root cause identified:** v2 config file (`ib2_0.json`) missing `"associations"` section entirely. Without Lifeline (Group 1) association:
- Device never auto-reports position to controller after movement
- Z-Wave JS UI only gets position via polling (unreliable)
- Home Assistant shows "unknown" because no unsolicited reports received

**Key findings:**
- v3 config has proper Lifeline association (Group 1, maxNodes: 1, isLifeline: true)
- v2 config identical to upstream zwave-js database (both missing associations)
- Both v2/v3 use Multilevel Switch CC; hardware capable of reporting
- v2 firmware does NOT support Parameter 4 (Default ON Value) - v3-only feature

**Recommended fix:** Add associations section to v2 config:
```json
"associations": {
  "1": {
    "label": "Lifeline",
    "maxNodes": 1,
    "isLifeline": true
  }
}
```

**Implementation steps:**
1. Edit `/opt/docker/home-assistant/zwave/.config-db/devices/0x0287/ib2_0.json`
2. Add associations section after firmwareVersion
3. Restart zwave-js-ui container
4. Re-interview all v2 nodes to apply new config
5. Test position reporting after local/remote commands

**Parameter 4 workaround (v2 lacks configurable stop point):**
- Create HA scripts for "open to preferred position" (e.g., 50%)
- Use Alexa routines calling HA scripts instead of raw Z-Wave commands
- Consider template cover wrappers to override default "open" behavior
- Native v2 behavior: Open=99 (fully open), Close=0 (no override possible)

**Research artifacts:**
- Full report: `/opt/docker/home-assistant/iblinds-v2-research-report.md`
- Upstream comparison: Both v2/v3 configs match zwave-js master branch
- Compat flags reviewed: treatSetAsReport (not applicable), manualValueRefreshDelayMs (not the fix), commandClasses.remove (optional for Binary Switch)

**Confidence:** HIGH - Association group is standard Z-Wave feature, config-only fix, reversible, low risk.

### 2026-04-15: iBlinds v2 Z-Wave capabilities (fw 1.65)

**Node survey:** v2 nodes (67, 71, 72, 103, 106, 107) — confirmed from d5eac29d.jsonl cache.

**CCs confirmed on node 71 (representative):**
- `0x85` Association CC v2 — **SUPPORTED** (key finding: upstream config had no `associations` block, so lifeline was never set up)
- `0x59` Association Group Info CC v2 — SUPPORTED
- `0x26` Multilevel Switch CC v4 — SUPPORTED (position control)
- `0x25` Binary Switch CC v2 — SUPPORTED but **unlinked** from cover position (same issue as v3)
- `0x80` Battery CC v1 — SUPPORTED
- Interview stage: Complete; security: none (no S0/S2)

**Upstream db status:** `zwave-js/zwave-js` GitHub `ib2_0.json` is identical to our local copy — just 1 param, no associations, no compat. Upstream has NOT fixed this.

**Root cause of "unknown" position:** No `associations` block in config → Z-Wave JS never adds controller to Group 1 Lifeline → device never sends unsolicited reports → position stays unknown indefinitely.

**Config changes made to `zwave/.config-db/devices/0x0287/ib2_0.json`:**
1. Added `associations.1` (Lifeline, maxNodes=1, isLifeline=true) — triggers auto-setup during re-interview
2. Added `compat.treatSetAsReport: ["Multilevel Switch"]` — handles fw that sends SET instead of REPORT via lifeline
3. Added `compat.commandClasses.remove: Binary Switch (endpoints: *)` — removes unlinked CC, prevents duplicate HA entities

**Action required:** Re-interview all 6 v2 nodes in Z-Wave JS UI (Node → Actions → Re-interview) to apply lifeline association.

**"Open goes to 100%" issue:** NO Z-Wave config fix possible. v2 has only 1 parameter (torque); there is no "Default ON Value" equivalent. Fix must live in HA — always send explicit position value (e.g., 99) instead of binary Cover Open service.

**No compat flag for position mapping exists** in the current zwave-js CompatConfig schema. The `disableStatefulGet`, `manualValueRefreshDelayMs`, and similar flags don't address the no-report problem; only Lifeline + `treatSetAsReport` does.
