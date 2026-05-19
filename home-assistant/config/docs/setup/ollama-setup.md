# Ollama Setup Guide

This guide covers deploying and configuring Ollama as a local LLM server for Home Assistant AI integrations.

## Overview

Ollama provides on-premise LLM capabilities for:
- **Conversation agents** — voice assistant chat via HA Assist pipeline
- **Device control actions** — natural language commands for smart home control
- **Dual-config pattern** — separate Ollama integration instances for chat vs. control

This setup uses `qwen3:8b` — stronger reasoning and structured output quality compared to `llama3.2:3b`, at acceptable RAM usage (~5GB active). Previously used `llama3.2:3b` (still valid for very memory-constrained environments).

---

## 1. Start Ollama

Use the Makefile target to start Home Assistant + Ollama:

```bash
make ollama
```

Then pull the model:

```bash
make ollama-pull   # pulls qwen3:8b (configured in Makefile)
```

This brings up:
- `home-assistant` container (host networking)
- `ollama` container (bridge network + exposed port 11434)

**Verify container is running:**

```bash
docker ps | grep ollama
```

Expected output:
```
CONTAINER ID   IMAGE                  ... PORTS                      NAMES
abc123...      ollama/ollama:latest   ... 0.0.0.0:11434->11434/tcp   ollama
```

---

## 2. First-Run: Pull the Model

On first startup, Ollama has no models downloaded. Pull `qwen3:8b`:

```bash
docker exec ollama ollama pull qwen3:8b
```

**Expected output:**
```
pulling manifest
pulling model...
success
```

**Verify model availability:**

```bash
docker exec ollama ollama list
```

Expected output:
```
NAME              ID              SIZE      MODIFIED
qwen3:8b        abc123...       4.7 GB    2 minutes ago
```

> **Note:** `qwen3:8b` requires ~5GB RAM when active (qwen3:8b; ~4GB for qwen3:4b fallback). Monitor with `docker stats ollama`. If memory-constrained, fall back to `llama3.2:3b` (~2GB).

---

## 3. Configure in Home Assistant

### Add Ollama Integration (First Instance)

1. **Navigate:** Settings → Devices & Services → Add Integration
2. **Search:** "Ollama"
3. **Configure:**
   - **Host:** `http://localhost:11434`
   - **Name:** `Ollama Chat`
   - **Model:** `qwen3:8b`
4. **Submit** — integration added

### Add Second Ollama Integration

Repeat the process for a second instance:

1. Settings → Devices & Services → Add Integration → Ollama
2. **Configure:**
   - **Host:** `http://localhost:11434`
   - **Name:** `Ollama Control`
   - **Model:** `qwen3:8b`
3. **Submit**

**Why two instances?**
- **Ollama Chat:** Dedicated to conversation agent duties (Assist pipeline)
- **Ollama Control:** Dedicated to device control actions (scripts, automations)

Separating chat from control prevents cross-contamination of context and allows independent tuning (e.g., different temperature/top_p settings per use case).

---

## 4. Wire Ollama Chat to Assist Pipeline

### Create Voice Assistant

1. **Navigate:** Settings → Voice Assistants
2. **Add Assistant:**
   - **Name:** `Ollama Assistant`
   - **Conversation Agent:** `Ollama Chat` (select from dropdown)
   - **Text-to-Speech:** Choose preferred TTS engine (e.g., Google, Piper)
   - **Speech-to-Text:** Choose preferred STT engine (e.g., Whisper, Google)
3. **Save**

### Test Conversation Agent

Use the **Assist** panel (top-right menu → Assist) to test:

**Example prompts:**
- "What's the weather today?"
- "Tell me a joke"
- "What time is it?"

Expected: Ollama Chat responds via the assistant pipeline.

---

## 5. Using Ollama Control (Device Actions)

The second integration (`Ollama Control`) is available for use in:
- **Scripts** — call `conversation.process` service with `agent_id: conversation.ollama_control`
- **Automations** — trigger natural language device commands
- **HA AI Task** — experimental feature for agent-based device control

**Example script:**

```yaml
# Example: Process a natural language command with Ollama Control
script:
  ollama_device_command:
    alias: "Ollama Device Command"
    sequence:
      - action: conversation.process
        data:
          agent_id: conversation.ollama_control
          text: "{{ command }}"
```

**Usage:**

```yaml
# Call from an automation
action: script.ollama_device_command
data:
  command: "Turn on the kitchen lights and set them to 50% brightness"
```

---

## 6. Configuration Options

### Environment Variables

Ollama behavior can be tuned via environment variables in `docker-compose.ollama.yml`:

```yaml
environment:
  OLLAMA_HOST: 0.0.0.0:11434          # Bind address
  OLLAMA_MODELS: /root/.ollama        # Model storage path (default)
  OLLAMA_NUM_PARALLEL: 1              # Max concurrent requests
  OLLAMA_MAX_LOADED_MODELS: 1         # Keep 1 model in memory
```

**Restart required after changes:**

```bash
docker restart ollama
```

### Model Selection

To use a different model:

1. Pull the new model:
   ```bash
   docker exec ollama ollama pull <model-name>
   ```

2. Update HA integration:
   - Settings → Devices & Services → Ollama Chat → Configure
   - Change **Model** dropdown to new model
   - Save

**Recommended models:**
- `qwen3:8b` — **Default.** Strong reasoning + structured output, ~5GB RAM. Supports HA's "Think before responding" toggle for enhanced reasoning.
- `qwen3:4b` — Lighter qwen3 variant, ~4GB RAM
- `llama3.2:3b` — Lightweight fallback for memory-constrained environments (~2GB)
- `llama3.2:1b` — Ultra-lightweight for slowest hardware
- `mistral:7b` — Alternative 7B option; similar profile to qwen3:8b
- `phi3:mini` — Fast, good for device control tasks

---

## 7. Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker logs ollama --tail 50
```

**Common issues:**
- Port 11434 already in use → Change `OLLAMA_PORT` in `.env`
- Volume mount permission error → Verify `./ollama/models` directory exists

### HA Can't Connect to Ollama

**Symptoms:** Integration setup fails with "Connection refused"

**Verify Ollama is reachable from HA container:**

```bash
docker exec home-assistant curl -s http://localhost:11434/api/version
```

Expected output:
```json
{"version":"0.x.x"}
```

**If connection fails:**
- HA uses **host networking** — `localhost:11434` should resolve directly to host port
- Verify Ollama port binding: `docker ps | grep ollama` shows `0.0.0.0:11434->11434/tcp`
- Check firewall rules if running on remote host

### Model Inference is Slow

**Expected behavior:** `qwen3:8b` on CPU takes 10-20 seconds for first response (model load), 2-5 seconds for subsequent responses.

**If slower than expected:**
- Check CPU usage: `docker stats ollama`
- Reduce concurrent requests: Set `OLLAMA_NUM_PARALLEL=1` in compose file
- Use a smaller model: `llama3.2:1b` or `phi3:mini`

### Model Not Found in HA Dropdown

**Symptoms:** Integration config shows "No models available"

**Verify model is pulled:**
```bash
docker exec ollama ollama list
```

**If empty:**
```bash
docker exec ollama ollama pull qwen3:8b
# or
make ollama-pull
```

**Restart HA integration:**
- Settings → Devices & Services → Ollama Chat → Reload

---

## 8. Maintenance

### Update Ollama

Pull latest Ollama image and restart:

```bash
make down
docker pull ollama/ollama:latest
make ollama
```

### Update Models

Re-pull a model to get the latest version:

```bash
docker exec ollama ollama pull qwen3:8b
```

### Migrate from llama3.2:3b to qwen3:8b

If you previously used `llama3.2:3b`, here's the upgrade path:

1. Pull the new model:
   ```bash
   docker exec ollama ollama pull qwen3:8b
   ```

2. Update **both** HA integrations:
   - Settings → Devices & Services → **Ollama Chat** → Configure → Model → `qwen3:8b` → Save
   - Settings → Devices & Services → **Ollama Control** → Configure → Model → `qwen3:8b` → Save

3. Test structured output (evening summary automation or Assist):
   ```bash
   # Verify qwen3:8b loads cleanly
   docker exec ollama ollama run qwen3:8b "Respond with JSON: {\"status\": \"ok\"}"
   ```

4. Optionally remove old model to free disk:
   ```bash
   docker exec ollama ollama rm llama3.2:3b
   ```

### Remove Unused Models

List models:
```bash
docker exec ollama ollama list
```

Remove a model:
```bash
docker exec ollama ollama rm <model-name>
```

---

## References

- **Ollama Docs:** https://github.com/ollama/ollama/blob/main/docs/api.md
- **HA Ollama Integration:** Settings → Devices & Services → Ollama
- **HA Conversation Agent:** https://www.home-assistant.io/integrations/conversation/
- **Model Library:** https://ollama.com/library

---

**Last Updated:** 2026-04-15  
**Maintained By:** Linus (Integration Specialist)
