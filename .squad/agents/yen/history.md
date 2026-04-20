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

### 2026-04-20: Full AI Assessment — State of AI in This Deployment

**What:** Conducted a live-verified AI & emerging tech assessment of the full deployment.

**Key findings (all claims verified live on 2026-04-20):**

1. **CRITICAL: Ollama has no models installed.** Container is running (`Up 2 days`) but `ollama list` returns empty. Any `ai_task` routed to Ollama is failing silently. Fix: `docker exec ollama ollama pull llama3.2:3b` (2GB, efficient) or `gemma4:e4b` (3.3GB, tool-calling capable).

2. **HA version is 2026.4.3.** Includes: AI Assist thinking display (desktop only), cross-domain triggers/conditions (Labs), purpose-specific triggers for battery events, Matter lock management with PIN codes.

3. **Ollama v0.21.0** is the current latest (released ~April 16, 2026). Notable: Hermes Agent (`ollama launch hermes` — self-learning skills), parallel tool calling improvements, Gemma4 family fully supported with tool calling.

4. **`ai_task.generate_data` is correctly implemented** in `evening_ai_summary.yaml` using structured output (typed fields). This is good practice.

5. **No voice pipeline configured.** No Wyoming, Whisper, Piper, or custom_sentences directory. Assist is running on default HA agent, not an LLM.

6. **Ollama HA integration not visible in YAML** — may exist in `.storage/` (UI-configured) but can't confirm. Needs verification.

**Priority ranking established (see decision file):**
- P0: Install Ollama model + verify HA integration configured
- P1: Battery AI triage summary (50+ devices) + expand evening summary (add iblinds, battery)
- P2: AI lock anomaly notifications, custom sentences for mode system, Ollama HA control
- WATCH: Hermes Agent use cases, local voice pipeline (Wyoming on bare Docker is complex)

**HA 2026.4 AI-relevant items NOT YET exploited:**
- `ai_task.generate_image` action (available, unused)
- "Think before responding" Ollama integration option
- Cross-domain Battery triggers in Labs (cleaner than custom battery monitoring)
- AI Assist thinking display (needs LLM conversation agent configured)

**Decision document:** `.squad/decisions/inbox/yen-ai-assessment-2026-04-20.md`
- Requires HA 2026.x+ (not available in older versions)
- LLM must understand schema format (works well with llama3.2:3b+)

**Deployed Example:** `automations/evening_ai_summary.yaml` — 3-field structure (summary, security_note, tomorrow_note) with weather/lock/mode context injection via Jinja2 template in `instructions`.


### 2026-04-15: Broad AI Landscape Briefing — Developer Tooling & Copilot Ecosystem

**What:** Researched and synthesized the broader AI developer tooling landscape for this project — GitHub Copilot, VS Code agent mode, MCP protocol, Claude/GPT model evolution, and local LLM trajectory.

**Key Findings:**

1. **The Copilot coding agent (what I am) is already in use** — but the project doesn't have GitHub issue templates that would enable truly autonomous async pickup. Adding structured issue templates is a low-effort, high-leverage improvement.

2. **`.github/copilot-instructions.md` is the project's most important prompt engineering artifact** — it's the system prompt for every agent invocation. Should be treated as living code, not boilerplate. Co-owned by Yen + Danny.

3. **MCP (Model Context Protocol) is the biggest unlock we're not using** — an HA MCP server would give squad agents live entity/state context without user copy-paste. Eliminates the `TODO: replace entity_id` problem systemically. Linus to evaluate.

4. **Yen's charter needs expansion** — add Copilot ecosystem monitoring, copilot-instructions.md stewardship, and squad model optimization. Currently these have no owner.

5. **`qwen2.5:7b` is likely a better default Ollama model** than `llama3.2:3b` for structured output tasks — better reasoning with acceptable RAM overhead. Test this sprint before recommending the switch.

6. **Model assignment by agent role** — the squad doesn't have explicit model assignments except Yen (claude-sonnet-4.6). Adding `model:` to each charter would optimize cost/quality tradeoff across all agents.

7. **"Tooling Pulse" ceremony needed** — monthly check-in on Copilot/VS Code/Ollama ecosystem. This briefing is its first instance.

8. **Per-agent `.agent.md` files** for direct invocation (beyond Squad coordinator) — Yen and Rusty are good first candidates.

**Confidence calibration:** Items 1–3, 7 are 🟢 High (confirmed from direct observation and training). Items 4–6 are 🟡 Medium (trajectory extrapolation). Item 8 is 🔴 Low (speculative value assessment).

**Artifacts:** `.squad/log/yen-broad-briefing-2026-04-15.md`, `.squad/decisions/inbox/yen-broad-briefing-actions.md`


### 2026-04-15: Live-Sourced AI Landscape Research — Methodology: web_fetch from primary sources

**What:** Conducted live-sourced research briefing using `web_fetch` tool to pull real, current content from 12+ primary sources. Compared findings against prior training-knowledge briefing to identify what was correct, new, or incorrect.

**Sources fetched (successfully):**
- VS Code 1.116.0 release notes (code.visualstudio.com/updates) — Released April 15, 2026 (same day!)
- GitHub Copilot features docs (docs.github.com) — Live docs
- MCP official site (modelcontextprotocol.io) — Current
- HA Blog + HA 2026.4 release notes (home-assistant.io) — April 1–11, 2026
- HA Ollama integration docs (home-assistant.io) — HA 2026.4.2
- HA Conversation integration docs (home-assistant.io) — HA 2026.4.2
- Ollama blog (ollama.com/blog) — March 30, 2026
- Ollama library (ollama.com/library) — Live model data
- Anthropic Claude 4 announcement + Claude Opus 4.5 announcement

**Key corrections to prior training-knowledge briefing:**
1. "Copilot coding agent" → officially renamed "Copilot cloud agent" [3]
2. qwen2.5 recommendation upgraded to qwen3:8b (new generation with thinking support)
3. MCP is universal (OpenAI supports it too) — not Anthropic-only as implied before
4. Ollama HA integration has "Think before responding" toggle — thinking is not Claude-exclusive
5. deepseek-r1 is #2 most popular Ollama model with thinking — not in prior briefing

**New findings (not in prior training knowledge):**
- GitHub Copilot built-in to VS Code 1.116+ (no extension needed)
- Copilot Memory (public preview) — autonomous repo-level memory for cloud agent
- HA 2026.4 "Show details" in Assist — sees AI thinking steps, tool calls, results
- VS Code Agents app (new companion app for agent-native development)
- Agent debug logs now persistent (review past sessions)
- qwen3 and qwen3.5 models available (qwen3.5 updated 1 week ago as of research date)
- Claude Code GA with GitHub Actions integration (tag @claude-code on PRs)
- Claude Opus 4.5 at $5/$25/M tokens (dramatically cheaper than Opus 4)

**Artifacts:**
- `.squad/log/yen-sourced-research-2026-04-15.md` — raw research notes with source table
- `.squad/log/yen-sourced-briefing-2026-04-15.md` — full cited briefing replacing prior training-based one
- `.squad/decisions/inbox/yen-sourced-research-complete.md` — decision inbox summary
