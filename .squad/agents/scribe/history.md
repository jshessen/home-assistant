# Scribe — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Session Logger
- **Joined:** 2026-04-14T17:06:50.079Z

## Learnings

### 2026-04-16: Triage of uncommitted files

**Uncommitted file assessment:**
- `.squad/agents/danny/history.md` — TRACKED (team learning record - Nick Fury's battery dashboard review insights)
- `home-assistant/config/alexa.yaml` — TRACKED (legitimate config simplification - moved helper entities to new package)
- `home-assistant/config/packages/alexa_helpers.yaml` — TRACKED (new package for Alexa monitoring helpers: template sensors, input_datetime, counter, rest_command, automations, scripts)
- `home-assistant/config/data/` — GITIGNORED (runtime artifacts; contains developer.amazon.com.har HAR file from Alexa testing)

**Actions taken:**
- Staged danny/history.md, alexa.yaml, alexa_helpers.yaml for commit
- Confirmed data/ directory already gitignored in both root and config/ .gitignore files
- Created retroactive orchestration log for battery dashboard work (coordinator inline, Nick Fury's post-review findings)

### 2026-04-16: Retroactive orchestration log

Created `/opt/docker/home-assistant/.squad/orchestration-log/2026-04-15T18-00-00Z-coordinator-battery-dashboard.md` to document:
- Coordinator's inline work (protocol violation - should have spawned via task tool)
- Battery Details view implementation (commit 2024949)
- Nick Fury's post-review findings: two bugs (folded YAML scalars breaking markdown tables, glob pattern matching failure)
- Architectural learning on YAML block scalar choice in Lovelace markdown cards

<!-- Append learnings below -->
