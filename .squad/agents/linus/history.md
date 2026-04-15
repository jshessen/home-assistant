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
