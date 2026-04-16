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
