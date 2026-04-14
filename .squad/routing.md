# Work Routing

How to decide who handles what. This table is authoritative — when two agents could plausibly own a domain, the primary column wins unless the task is explicitly in the secondary's core expertise.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| HA automation YAML | Rusty | Files in `automations/`, entries in `automations.yaml` |
| HA script YAML | Rusty | Files in `scripts/` |
| Lovelace dashboards | Rusty | Files in `lovelace/`, `lovelace.yaml` |
| Input helpers (structural) | Rusty | `input_boolean.yaml`, `input_select.yaml`, `input_number.yaml`, `input_datetime.yaml` — schema/structure changes |
| Input helpers (template-driven logic) | Basher | Helper YAML where value is derived from Jinja2 expressions |
| Jinja2 templates | Basher | Files in `templates/`, inline `template:` sensor blocks |
| Template sensors | Basher | `sensor:` or `binary_sensor:` blocks using Jinja2 |
| Helper logic (conditions, choose, variables) | Basher | `condition:` blocks, `choose:` branches, `variables:` maps |
| Packages | Rusty or Basher | Rusty if automation-primary; Basher if template-primary |
| Device integrations | Linus | Z-Wave, Zigbee, HA integration config |
| Z-Wave config | Linus | Files in `zwave/`, Z-Wave JS UI settings |
| Zigbee config | Linus | Files in `zigbee2mqtt/` |
| MQTT config | Linus | Files in `mosquitto/` |
| Docker Compose / Makefile | Linus | `docker-compose*.yml`, `Makefile`, `config.d/` |
| Debugging, log analysis | Livingston | HA logs, Z-Wave logs, entity ID research, failure diagnosis |
| Entity ID research | Livingston | Discovering entity names, verifying states, mapping device IDs |
| System architecture decisions | Danny | ADRs, multi-file refactors, design reviews, cross-cutting concerns |
| Technology trade-off analysis | Danny | Stack selection, integration pattern evaluation |
| Session logging | Scribe | Automatic — never needs explicit routing |
| Decision merging | Scribe | Moves `decisions/inbox/` files into `decisions.md` |
| Git commits of `.squad/` files | Scribe | Always `mode: "background"` |
| GitHub issue triage | Saul | Issues, milestones, labels, issue templates, GitHub project board |
| PR lifecycle monitoring | Saul | PR status, changelogs, release tags, branch hygiene |
| `.gitignore` / `.gitattributes` | Saul | Scope boundaries, merge driver decisions, exclusion rules |
| VS Code workspace config | Saul | `home-assistant.code-workspace`, `.vscode/` settings, custom YAML tags |
| Repo scope decisions | Saul | What paths belong in source control, what's excluded, external repo boundaries |
| Git clean-up | Saul | Stale branches, commit history organization, pre-commit conventions |
| Ralph work queue monitoring | Ralph | Issues with `squad` label — scan board, surface work, keep team moving |
| AI/ML integration research | Yen | Ollama, LocalAI, Whisper, conversation agents, HA AI Task |
| LLM-assisted template/prompt work | Yen | Prompt engineering, Jinja2 optimization via AI techniques |
| Emerging tech evaluation | Yen | New HA integrations, custom components, agent frameworks |
| Team tech briefings / skill training | Yen | Codifying new patterns as `.squad/skills/` entries |
| AI-assist opportunity review | Yen | Reviewing existing work for AI-enhancement candidates |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage: analyze issue, assign `squad:{member}` label | Danny (Lead) |
| `squad:rusty` | Pick up and complete automation/script/dashboard work | Rusty |
| `squad:linus` | Pick up and complete integration/infra work | Linus |
| `squad:basher` | Pick up and complete template/logic work | Basher |
| `squad:livingston` | Pick up and complete debugging/diagnostics work | Livingston |
| `squad:danny` | Pick up and complete architecture/design work | Danny |
| `squad:saul` | Pick up and complete repo hygiene/GitHub project management work | Saul |
| `squad:ralph` | Monitor, triage, or escalate issue/PR work | Ralph |
| `squad:yen` | Pick up and complete AI/ML integration or tech research work | Yen |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, **Danny** triages it — analyzing content, assigning the right `squad:{member}` label, and commenting with triage notes.
2. When a `squad:{member}` label is applied, that member picks up the issue in their next session.
3. Members can reassign by removing their label and adding another member's label.
4. The `squad` label is the "inbox" — untriaged issues waiting for Lead review.

## Rules

1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a feature is being built, spawn the downstream agent to prepare simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. Danny handles all `squad` (base label) triage.

## Quick Reference: Agent → Domain

| Agent | Primary Domain |
|-------|---------------|
| Danny | Architecture, decisions, cross-cutting reviews |
| Rusty | Automations, scripts, lovelace, input helpers (structural) |
| Linus | Device integrations, Z-Wave, Zigbee, MQTT, Docker/infra |
| Basher | Jinja2 templates, template sensors, helper logic |
| Livingston | Debugging, log analysis, entity ID research, diagnostics |
| Yen | AI/ML integrations, emerging tech, team training, prompt engineering |
| Scribe | Session logging, decision merging, `.squad/` git commits |
| Ralph | GitHub issue triage, PR lifecycle monitoring |

