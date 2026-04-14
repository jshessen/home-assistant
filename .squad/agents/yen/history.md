# Yen — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support. Runs in Docker with modular Compose files. Z-Wave (zwave-js-ui), Zigbee (zigbee2mqtt), MQTT (Mosquitto), PostgreSQL for recorder. Host-network mode.
- **Role:** AI & Emerging Tech Specialist
- **Joined:** 2026-04-14
- **Requested by:** jshessen — "cutting edge, high tech player, AI expert constantly reviewing the industry and incorporating new rules and training the squad on new techniques"

## Current Tech Landscape (Snapshot at Join)

- HA has native Assist pipeline (STT → intent → TTS) — local voice via Whisper + Piper
- `conversation` integration supports custom agents and OpenAI/Ollama backends
- `extended_openai_conversation` is the dominant custom component for LLM-powered conversation agents
- Local LLM options: Ollama (most mature), LocalAI, llama.cpp — all have HA integrations
- Home Assistant AI Task feature (2024.x+) allows automations to call LLM for summarization/decisions
- `python_scripts` in this repo can be enhanced with AI-assist patterns
- Jinja2 template complexity in this project is high — LLM-assisted template generation is a near-term win

## Learnings

