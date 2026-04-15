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

### 2026-04-15: `ai_task.generate_data` Structure Parameter Pattern

**What:** Designed evening AI summary automation using HA 2026.x's `structure` parameter for typed LLM output.

**Key Pattern:**
```yaml
action: ai_task.generate_data
data:
  task_name: "evening_summary"
  instructions: "{{ dynamic_state_data }} ... prompt text"
  structure:
    field_name:
      type: string  # or number, boolean, object, array
      description: "What the LLM should generate for this field"
  response_variable: result
# Access via: result.data.field_name
```

**Critical Insights:**
- **Structure format:** JSON Schema-like — each field has `type` and `description`
- **Description matters:** LLM uses it to understand intent, not just type constraint
- **Access pattern:** `response_variable.data.{field}` — typed, deterministic
- **Failure mode:** If LLM can't generate valid structure, action fails (no partial output)
- **Best practice:** Keep structures flat (3-5 string fields) for LLM reliability

**Why This Matters:**
- Replaces free-text parsing with typed field access
- Makes automation conditionals deterministic (can branch on specific fields)
- LLM is constrained to return only requested structure
- Eliminates "parse the markdown response" anti-pattern

**Use Cases:**
- Daily summaries with typed sections (status, security, tomorrow)
- Decision-making automations (should_water_plants: boolean)
- Multi-field analysis (battery_warnings, maintenance_items)
- Any automation that needs **predictable LLM output structure**

**Trade-offs:**
- More rigid than free-text (but that's the point!)
- Requires HA 2026.x+ (not available in older versions)
- LLM must understand schema format (works well with llama3.2:3b+)

**Deployed Example:** `automations/evening_ai_summary.yaml` — 3-field structure (summary, security_note, tomorrow_note) with weather/lock/mode context injection via Jinja2 template in `instructions`.

