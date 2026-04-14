# Skill: HA AI Integration Patterns

> Yen's distilled guide for integrating AI capabilities into this Home Assistant deployment.

## Overview

Home Assistant has matured significantly in the AI space. This skill covers what's available, what's worth implementing, and how to do it on this specific deployment (Docker, host-network, Z-Wave + Zigbee).

## Current HA AI Stack (2024+)

### Native: Assist Pipeline
The built-in voice assistant pipeline: **STT → Intent Recognition → Response → TTS**

- Fully local when using Whisper (STT) + Piper (TTS)
- `conversation` integration is the backend for intent handling
- Can be replaced with an LLM backend (OpenAI, Ollama) for natural-language understanding beyond the built-in intent parser

### Native: AI Task (HA 2024.x+)
Allows automations to call an LLM for tasks like:
- Summarization: `{{ ai_task.generate_data('summarize_sensor_data', ...) }}`
- Decision support in automations
- Text processing in Jinja2 templates (via `ai_task` template helper)

### Custom Components (HACS)

| Component | Purpose | Status in this repo |
|-----------|---------|---------------------|
| `extended_openai_conversation` | LLM-powered conversation agent (OpenAI/Ollama/LocalAI) | Not installed |
| `ollama` (native since HA 2024.3) | Local LLM via Ollama | Not installed |
| `whisper` (native) | Local STT | Not installed |
| `piper` (native) | Local TTS | Not installed |

---

## Integration Recipes for This Deployment

### Recipe 1: Local Voice (Whisper + Piper + Ollama)

**Prerequisites:** Ollama running on the host (Docker container or host process).

**Step 1: Add Ollama to Docker Compose**
Linus owns this — add to `docker-compose.yml` or create `docker-compose.ollama.yml`:
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ./ollama/models:/root/.ollama
    ports:
      - "11434:11434"
    # GPU pass-through (optional, requires nvidia-docker):
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]
    restart: unless-stopped
```

**Step 2: Configure in HA**
Go to Settings → Integrations → Add Integration → Ollama.
- Host: `http://localhost:11434` (HA uses host networking — localhost resolves)
- Model: `llama3.2` or `mistral` (balance of quality and speed)

**Step 3: Wire to Assist Pipeline**
Settings → Voice Assistants → Create a new assistant → set Conversation Agent to Ollama.

### Recipe 2: AI Task in Automations

```yaml
# Example: Summarize today's sensor activity in an evening notification
automation:
  - alias: "Evening AI Summary"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - action: ai_task.generate_data
        data:
          task_name: "evening_summary"
          instructions: >
            Summarize today's home activity based on the following data.
            Presence: {{ states('person.jeff') }}.
            Temperature range: {{ state_attr('sensor.outdoor_temp', 'min') }}–{{ state_attr('sensor.outdoor_temp', 'max') }}°F.
            Keep it to 2 sentences.
        response_variable: summary
      - action: notify.mobile_app_jeff
        data:
          message: "{{ summary.text }}"
```

### Recipe 3: LLM-Enhanced Jinja2 Templates

Basher can use `conversation.process` service to enrich template logic:
```yaml
# Ask the LLM for a friendly name for the current mode
- action: conversation.process
  data:
    agent_id: ollama  # or openai
    text: "Give a short friendly status message for 'away mode' in a smart home."
  response_variable: mode_description
```

---

## Prompt Engineering for HA Jinja2

### Principle: Specificity Over Cleverness
HA templates execute in milliseconds with no retry. Prompts for template generation must be:
1. **Exact about types:** "states() returns a string, not a number — always cast with | int(default)"
2. **HA-version aware:** "Use `action:` not `service:`, valid since HA 2024.8"
3. **Failure-aware:** "Always handle 'unavailable' and 'unknown' states"

### Canonical Template Prompt Structure
When asking an LLM to generate a HA Jinja2 template:
```
Generate a Home Assistant Jinja2 template for [task].
Constraints:
- states() returns strings; cast with | int(0) or | float(0.0)
- Always check: value not in ('unavailable', 'unknown') before using state
- Use is not none for undefined checks, not truthiness
- HA version: 2024.x (use action: not service:)
- Template renders in isolation — no Python imports available
```

---

## Evaluation Checklist for New AI Integrations

Before recommending any new AI integration to the team:

- [ ] Does it work with local LLMs (Ollama)? Prefer local over cloud for privacy
- [ ] Does it survive HA restart without re-auth?
- [ ] Does it add meaningful latency to automations?
- [ ] Is it maintained (last commit < 6 months)?
- [ ] Does it conflict with existing integrations (`spook`, `alarmo`, etc.)?
- [ ] Is it installable via HACS without custom repo?

---

## Current Opportunity Assessment (This Repo)

| Opportunity | Effort | Impact | Owner |
|-------------|--------|--------|-------|
| Local voice (Whisper+Piper+Ollama) | Medium (Linus: Docker, then HA config) | High — hands-free control | Yen→Linus |
| Evening AI summary notification | Low (Basher/Rusty) | Medium — useful daily | Yen→Rusty |
| Jinja2 optimization pass via LLM | Low (Basher) | Medium — reduce template complexity | Yen→Basher |
| AI-powered presence detection (pattern learning) | High | High | Yen→Danny (ADR first) |
| `extended_openai_conversation` install | Low | Medium — richer voice commands | Yen→Linus |

---

## References

- [HA Assist Pipeline docs](https://www.home-assistant.io/docs/assist/)
- [HA AI Task integration](https://www.home-assistant.io/integrations/ai_task/)
- [Ollama HA integration](https://www.home-assistant.io/integrations/ollama/)
- [extended_openai_conversation (HACS)](https://github.com/jekalmin/extended_openai_conversation)
- [Whisper HA integration](https://www.home-assistant.io/integrations/whisper/)
- [Piper HA integration](https://www.home-assistant.io/integrations/piper/)
