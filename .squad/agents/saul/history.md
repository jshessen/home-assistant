# Saul — Project Steward — History

## Project Context

- **Project:** home-assistant Docker setup (multi-root VS Code workspace)
- **User:** jshessen
- **Created:** 2026-04-14
- **Repo root:** `/opt/docker/home-assistant`
- **Config root:** `/opt/docker/home-assistant/home-assistant/config`

## What This Project Is

Multi-service Home Assistant deployment using Docker Compose with modular YAML includes. The workspace has 4 roots:
1. **Home Assistant Config** (`home-assistant/config/`) — main HA configuration
2. **External Connectors** (`home-assistant/ha-external-connector/`) — placeholder infrastructure
3. **Cloudflare Workers** (`home-assistant/cloudflare/`) — Authentik auth proxy
4. **Root** (`.`) — Docker Compose orchestration and Makefile commands

Sub-repos in the workspace (NOT owned by this project):
- `keymaster-github/` — external Z-Wave lock component (upstream repo)
- `pyonwater-github/` — external water meter library (upstream repo)

## Scope Boundaries (Known)

- **We own:** `home-assistant/config/`, `mosquitto/`, `zwave/` (config + settings), `zigbee2mqtt/data/` (config), `scripts/`, `secrets/` (contents excluded), `.squad/`, `docker-compose*.yml`, `Makefile`, `pyproject.toml`, `config.d/`
- **We do NOT own / should exclude:** `home-assistant/config/deps/` (Python cache), `home-assistant/config/.storage/` (HA runtime state), `home-assistant/config/home-assistant.log*` (logs), `home-assistant/config/backups/`, `keymaster-github/` and `pyonwater-github/` (external repos — they have their own .git)
- **Ambiguous / needs review:** `home-assistant/config/custom_components/` (HACS-managed components — some generated, some ours)

## Learnings

### 2026-04-14 — First run: repo hygiene audit

**State of .gitignore on arrival:**
- Very sparse. Covered: `secrets.yaml`, `known_devices.yaml`, `home-assistant.log`, `home-assistant_v2.db`, `*.db-journal`, `*.pid`, squad runtime dirs, squad-workstream.
- Critical gap: `secrets/` (Docker bind-mount directory) was NOT ignored. Active security risk.
- Missing: all HA runtime paths (path-qualified), Docker runtime state, Python artifacts, `.vscode/`, log variants, DB shm/wal/backup variants.

**What I added to .gitignore:**
- `secrets/` directory — highest priority security fix
- HA runtime: `.storage/`, `deps/`, `backups/`, `tts/`, `.cloud/`, `OZW_Log.txt`, path-qualified log and db variants
- External sub-repo guards: `keymaster-github/`, `pyonwater-github/`
- Docker runtime state: `postgres/data/`, `mosquitto/data/`, `mosquitto/logs/`, `zigbee2mqtt/data/log/`
- Python artifacts: `__pycache__/`, `*.py[cod]`, `.venv/`, `*.egg-info/`, `.pytest_cache/`, `htmlcov/`, `.coverage`, `coverage.xml`, `.mypy_cache/`
- Log variants: `*.log.*`, `*.log.fault`, `*.log.grep.txt`, `zwave/logs/`
- DB variants: `*.db-shm`, `*.db-wal`, `*.db.backup`
- `.vscode/` (user-local state; `.code-workspace` kept separately)

**What I added to .gitattributes:**
- EOL normalization: `*.yaml`, `*.yml`, `*.sh`, `*.py` → `text eol=lf`
- `*.json` → `text`
- `secrets/* -diff` — suppress secret content from diff output
- `*.db`, `*.db-shm`, `*.db-wal` → `binary`

**What I changed in home-assistant.code-workspace:**
- Added `!env_var scalar` to `yaml.customTags` (was missing, caused unnecessary warnings)

**Scope ambiguities / open questions left for user:**
1. `keymaster-github/` workspace folder references a path that doesn't exist on disk — stale or intentional?
2. `.vscode/` is now gitignored — user should confirm if any `.vscode/` files should be shared
3. Task container names use `homeassistant` (no hyphen) but the real container is `home-assistant` — probably broken tasks; flagged but not fixed (out of audit scope)

**Patterns to remember:**
- This repo uses `secrets/` as a Docker bind-mount directory, not a `secrets.yaml` at config root. Always check BOTH.
- `.ignore` file exists for ripgrep/fd — keep in sync with `.gitignore` where appropriate.
- `keymaster-github/` and `pyonwater-github/` are referenced in workspace/gitignore as position-holders even when not cloned; guard entries are correct defensive practice.

