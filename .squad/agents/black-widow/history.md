# Black Widow — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Integration Specialist
- **Joined:** 2026-04-14T17:06:50.077Z

## Learnings

<!-- Append learnings below -->

### 2026-04-20: Full infrastructure assessment

**Task:** Comprehensive audit of all Docker Compose services, Z-Wave, Zigbee, MQTT, secrets, networking.

**Critical active fix applied during assessment:**
- **Zigbee2MQTT restart loop (4+ days down):** Root cause = stale MQTT password in `zigbee2mqtt/data/configuration.yaml` that didn't match live broker credential. Error: `MQTT failed to connect, exiting... (Connection refused: Not authorized)`. Fixed by updating the password. Also fixed health check from `http://0.0.0.0:8080/health` → `http://localhost:8080/health` (0.0.0.0 is not a valid connect host) and increased start_period from 30s → 60s.
- **Key lesson:** When rotating MQTT credentials, ALL clients (zigbee2mqtt config, HA MQTT integration, etc.) must be updated atomically. Stale credentials cause silent restart loops.

**Key findings summary:**
1. `secrets/zigbee2mqtt` file is 0 bytes — ZIGBEE2MQTT_SECRET_FILE mount is a no-op. Credential is plaintext in configuration.yaml.
2. MQTT admin password is in plaintext in `config.d/mqtt.env` (flows into .env → docker-compose environment).
3. Z-Wave S2 keys are plaintext in `zwave/settings.json` — Z-Wave JS UI ecosystem limitation, no solution currently.
4. No MQTT ACL file — all authenticated clients have wildcard topic access.
5. MQTT port 1883 bound to 0.0.0.0 (all interfaces), not just localhost.
6. Ollama port 11434 bound to 0.0.0.0 (all interfaces) — local LAN can reach it.
7. All images use `:latest` — no version pinning.
8. Node 136 (Garage Door) has persistent S0 nonce expiry errors.
9. Node 106 (Guest Bedroom) has no name.
10. socket-proxy container is exited (Exited 255, 2 days ago).
11. portainer_agent container running but not in any compose file.

**Infrastructure health at assessment end:**
- HA: running (no healthcheck)
- zwave-js-ui: healthy
- mqtt: healthy  
- homeassistant-postgres: healthy
- zigbee2mqtt: fixed and running (was unhealthy/restarting)
- ollama: running (no healthcheck)

**Full assessment filed:** `.squad/decisions/inbox/linus-infra-assessment-2026-04-20.md`

### 2026-04-20: iBlinds v2 Alexa protocol chain investigation

**Question:** Why does "Alexa, open blinds" go to 100% on v2 but the iBlinds app goes to 50%?

**Protocol chain confirmed (all verified live):**
1. "Alexa, open [blind]" → Alexa `RangeController` "open" semantic → HA `cover.open_cover`
2. HA `ZWaveMultilevelSwitchCover.async_open_cover()` → `Multilevel Switch Set(99)` (99 = fully open in Z-Wave)
3. v2 device receives Set(99) → moves to 99% (no Parameter 4 to remap it)
4. iBlinds app sends `Multilevel Switch Set(50)` explicitly → both v2 and v3 go to 50%

**Key difference v2 vs v3 via Alexa:**
- v3 has Parameter 4 "Default ON Value" = 50 → firmware remaps incoming 99 to 50
- v2 has no Parameter 4 → 99 is executed literally

**ib2_0.json current state (2026-04-20):**
- ✅ Lifeline association (Group 1) — ALREADY APPLIED (since research report 2026-04-15)
- ✅ Binary Switch CC removal compat — ALREADY APPLIED
- ⚠️ `treatSetAsReport: ["Multilevel Switch"]` — added but effect on Multilevel Switch CC uncertain; research report says it only works for Binary Switch CC and Thermostat Mode CC

**Fix options ranked:**
1. **Template Cover** (best) — override `open_cover` to call `set_cover_position(50)`, pass through everything else; preserves all Alexa utterances
2. **Script** — single script sets all v2 blinds to 50%; simpler but loses per-blind Alexa control
3. **Alexa Routine** — no HA changes; brittle with NLP conflicts

**Source verified:** 
- HA Alexa cover docs: https://www.home-assistant.io/integrations/alexa.smart_home/
- HA zwave_js cover source: github.com/home-assistant/core/blob/dev/homeassistant/components/zwave_js/cover.py
- Full report: `.squad/decisions/inbox/linus-iblinds-alexa-protocol.md`

**Pending action:** 6 v2 nodes (67, 71, 72, 103, 106, 107) need re-interview in Z-Wave JS UI to activate Lifeline association. Template cover implementation needed for Alexa fix.

### 2026-04-21: Infrastructure audit

**Task:** Targeted re-audit of all compose files, env files, device paths, secrets, MQTT config, and container health.

**Active issues found and fixed:**
1. **zigbee2mqtt unhealthy (running container using stale healthcheck):** Container was never recreated after prior healthcheck fix. Running container still had OLD `http://0.0.0.0:8080/health` baked in (returns 404). Fixed compose to `http://localhost:8080/` (root URL works; `/health` endpoint does not exist in z2m). Container needs manual recreation.
2. **zwave SESSION_SECRET_FILE path mismatch:** Secret name `zwave_secrets` mounts at `/run/secrets/zwave_secrets` (underscore). Env var pointed to `/run/secrets/zwave-secrets` (hyphen). Secret was never being read. Fixed env var to use underscore. Container needs manual recreation.
3. **docker-compose.yml stale `zwave_secrets` secret:** Pointed to `./secrets/hacs` which doesn't exist. Was silently overridden by zwave compose. Replaced with `secrets: {}`.
4. **Port comment typo:** `# Web UI:wq` (vim artifact) in zwave compose fixed.

**Key lessons:**
- When a compose file change only affects healthcheck config, the CONTAINER must be recreated (not just restarted) for Docker to apply the new healthcheck. `docker compose up -d` only recreates if the container definition changes; healthcheck-only changes may not trigger recreation.
- Docker mounts secrets at `/run/secrets/{secret_name}` using the secret's **name** in the compose YAML, not the filename. When name has underscores, path has underscores.
- zigbee2mqtt's health endpoint is `/` (root), not `/health` — `/health` returns 404.
- `docker inspect <container> --format '{{json .Config.Healthcheck}}'` shows the RUNNING container's baked-in healthcheck, which may differ from the compose file if the container hasn't been recreated.

**Warnings still outstanding:**
- secrets/zigbee2mqtt is 0 bytes — credential plaintext in z2m config
- HA MQTT integration still uses `hacs` credential (migration incomplete)
- zigbee2mqtt log_level is `debug` in production
- HA container has no healthcheck
- Ollama port exposed to all interfaces (0.0.0.0)

**Infrastructure health at audit end:**
- home-assistant: running (no healthcheck, 3 hours uptime)
- zwave-js-ui: healthy (3 days)
- mqtt: healthy (27 min — restarted recently)
- homeassistant-postgres: healthy (3 days)
- zigbee2mqtt: UNHEALTHY (running, MQTT connected, but healthcheck failing — needs recreation)
- ollama: running, no healthcheck (3 days)
- portainer_agent: running outside compose management

**Full audit filed:** `.squad/decisions/inbox/linus-infra-audit-2026-04-21.md`

---

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

### 2026-04-15: battery-state-card entities+filter exclude interaction (v8 fix)

**Problem:** 3 rechargeable devices (Sparky, Galaxy Watch, Patricia's phone) were explicitly listed in `entities:` blocks with `charging_state` config, then also excluded from `filter.exclude` via `name: entity_id` rules to prevent duplicates. Result: all 3 were invisible; fleet counter showed 35 instead of 38.

**Root cause (source-confirmed):**
In battery-state-card v4.2.2, `processExcludes()` iterates over **all** batteries — both explicit entities AND filter-discovered ones. It does NOT check whether an entity came from the explicit `entities:` block. The `explicitEntities` Set is only used in `processBatteryNotesDedup()`, not in `processExcludes()`.

The `is_permanent` getter: `return "state" != this.config.name && !this.config.name.startsWith("computed.")` — so `entity_id` filters are **permanent**, meaning matched entities are pushed to a delete list and removed from the batteries map entirely.

**Execution order:**
1. Constructor: `processExplicitEntities()` → adds entities, sets `explicitEntities`
2. `update()` (first run): `processGroupEntities()` → `processIncludes()` → `processExcludes()`
3. `processIncludes()` does `if(this.batteries[e]) return` — explicit entities skip the include pass ✓
4. `processExcludes()` with `entity_id` exclude → permanent deletion overwrites step 1 ✗

**Fix:** Removed the 3 `entity_id` exclude entries and their YAML anchors (`&rechargeable-excl-*`). The include filter naturally skips explicit entities already in the batteries map. No duplicates. `charging_state` config on explicit entities is preserved.

**Key insight:** `entity_id` excludes are for removing unwanted filter-discovered entities, NOT for deduplication with explicit entities. Explicit entities self-deduplicate via the `processIncludes` early-return guard.

**Confidence:** HIGH — confirmed from minified JS source, not guessed.
