# Ceremonies

> Team meetings that happen before or after work. Each squad configures their own.

## Design Review

| Field | Value |
|-------|-------|
| **Trigger** | auto |
| **When** | before |
| **Condition** | multi-agent task involving 2+ agents modifying shared systems |
| **Facilitator** | lead |
| **Participants** | all-relevant |
| **Time budget** | focused |
| **Enabled** | ✅ yes |

**Agenda:**
1. Review the task and requirements
2. Agree on interfaces and contracts between components
3. Identify risks and edge cases
4. Assign action items

---

## Retrospective

| Field | Value |
|-------|-------|
| **Trigger** | auto |
| **When** | after |
| **Condition** | build failure, test failure, or reviewer rejection |
| **Facilitator** | lead |
| **Participants** | all-involved |
| **Time budget** | focused |
| **Enabled** | ✅ yes |

**Agenda:**
1. What happened? (facts only)
2. Root cause analysis
3. What should change?
4. Action items for next iteration

---

## Yen Tech Briefing

| Field | Value |
|-------|-------|
| **Trigger** | periodic |
| **When** | after |
| **Condition** | user asks "what's new in HA AI?" or at start of any Yen-assigned session |
| **Facilitator** | yen |
| **Participants** | all-relevant |
| **Time budget** | focused |
| **Enabled** | ✅ yes |

**Agenda:**
1. New or updated HA AI integrations since last briefing (Ollama, Whisper, Assist, conversation agents, HA AI Task)
2. Relevant techniques from the broader AI/agent tooling landscape
3. Specific opportunities identified in this project (templates, automations, voice control)
4. Recommended action items — only what moves the needle, no noise

**Output:** A concise briefing note in `.squad/log/` titled `yen-tech-briefing-{date}.md`. If a new pattern warrants a skill, Yen creates it in `.copilot/skills/` and notifies the coordinator.
