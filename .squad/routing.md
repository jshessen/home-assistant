# Work Routing

How to decide who handles what. This table is authoritative — when two agents could plausibly own a domain, the primary column wins unless the task is explicitly in the secondary's core expertise.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| HA automation YAML | Iron Man | Files in `automations/`, entries in `automations.yaml` |
| HA script YAML | Iron Man | Files in `scripts/` |
| Lovelace dashboards | Iron Man | Files in `lovelace/`, `lovelace.yaml` |
| Input helpers (structural) | Iron Man | `input_boolean.yaml`, `input_select.yaml`, `input_number.yaml`, `input_datetime.yaml` — schema/structure changes |
| Input helpers (template-driven logic) | Doctor Strange | Helper YAML where value is derived from Jinja2 expressions |
| Jinja2 templates | Doctor Strange | Files in `templates/`, inline `template:` sensor blocks |
| Template sensors | Doctor Strange | `sensor:` or `binary_sensor:` blocks using Jinja2 |
| Helper logic (conditions, choose, variables) | Doctor Strange | `condition:` blocks, `choose:` branches, `variables:` maps |
| Packages | Iron Man or Doctor Strange | Iron Man if automation-primary; Doctor Strange if template-primary |
| Device integrations | Black Widow | Z-Wave, Zigbee, HA integration config |
| Z-Wave config | Black Widow | Files in `zwave/`, Z-Wave JS UI settings |
| Zigbee config | Black Widow | Files in `zigbee2mqtt/` |
| MQTT config | Black Widow | Files in `mosquitto/` |
| Docker Compose / Makefile | Black Widow | `docker-compose*.yml`, `Makefile`, `config.d/` |
| Debugging, log analysis | Hawkeye | HA logs, Z-Wave logs, entity ID research, failure diagnosis |
| Entity ID research | Hawkeye | Discovering entity names, verifying states, mapping device IDs |
| System architecture decisions | Nick Fury | ADRs, multi-file refactors, design reviews, cross-cutting concerns |
| Technology trade-off analysis | Nick Fury | Stack selection, integration pattern evaluation |
| Session logging | Scribe | Automatic — never needs explicit routing |
| Decision merging | Scribe | Moves `decisions/inbox/` files into `decisions.md` |
| Git commits of `.squad/` files | Scribe | Always `mode: "background"` |
| GitHub issue triage | Captain America | Issues, milestones, labels, issue templates, GitHub project board |
| PR lifecycle monitoring | Captain America | PR status, changelogs, release tags, branch hygiene |
| Branch management | Captain America | ahead/behind checks, stale branches, branch cleanup plans |
| Release changelog management | Captain America | release notes drafts, changelog curation, release cut prep |
| `.gitignore` / `.gitattributes` | Captain America | Scope boundaries, merge driver decisions, exclusion rules |
| VS Code workspace config | Captain America | `home-assistant.code-workspace`, `.vscode/` settings, custom YAML tags |
| Repo scope decisions | Captain America | What paths belong in source control, what's excluded, external repo boundaries |
| Git clean-up / repo hygiene | Captain America | working tree cleanup checklists, non-destructive reconciliation plans, pre-commit conventions |
| Ralph work queue monitoring | Ralph | Issues with `squad` label — scan board, surface work, keep team moving |
| Async background tasks (tests, docs, deps) | @copilot | Routine mechanical work assigned via GitHub issue; not spawnable |
| AI/ML integration research | Vision | Ollama, LocalAI, Whisper, conversation agents, HA AI Task |
| LLM-assisted template/prompt work | Vision | Prompt engineering, Jinja2 optimization via AI techniques |
| Emerging tech evaluation | Vision | New HA integrations, custom components, agent frameworks |
| Team tech briefings / skill training | Vision | Codifying new patterns as `.squad/skills/` entries |
| AI-assist opportunity review | Vision | Reviewing existing work for AI-enhancement candidates |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage: analyze issue, assign `squad:{member}` label | Nick Fury (Lead) |
| `squad:iron-man` | Pick up and complete automation/script/dashboard work | Iron Man |
| `squad:black-widow` | Pick up and complete integration/infra work | Black Widow |
| `squad:doctor-strange` | Pick up and complete template/logic work | Doctor Strange |
| `squad:hawkeye` | Pick up and complete debugging/diagnostics work | Hawkeye |
| `squad:nick-fury` | Pick up and complete architecture/design work | Nick Fury |
| `squad:captain-america` | Pick up and complete repo hygiene/GitHub project management work | Captain America |
| `squad:ralph` | Monitor, triage, or escalate issue/PR work | Ralph |
| `squad:vision` | Pick up and complete AI/ML integration or tech research work | Vision |
| `squad:copilot` | Assign issue to GitHub Copilot coding agent for async work | @copilot |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, **Nick Fury** triages it — analyzing content, assigning the right `squad:{member}` label, and commenting with triage notes.
2. When a `squad:{member}` label is applied, that member picks up the issue in their next session.
3. Members can reassign by removing their label and adding another member's label.
4. The `squad` label is the "inbox" — untriaged issues waiting for Lead review.

## Rules

0. **Rule 0: The coordinator routes — it does not implement.** Producing domain artifacts inline (YAML, config, templates, charters, docs) is a routing failure. If the coordinator writes it, a squad member should have written it instead. No exceptions for "small" or "obvious" changes.
1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a feature is being built, spawn the downstream agent to prepare simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. Nick Fury handles all `squad` (base label) triage.
8. **gem-\* agents are not squad members.** Never use `gem-*` agentNames when spawning squad members — they discard the charter. Embed the full charter in the prompt; omit `agentName` (or use `"Explore"` for read-only tasks only).

## Quick Reference: Agent → Domain

| Agent | Primary Domain |
|-------|---------------|
| Nick Fury | Architecture, decisions, cross-cutting reviews |
| Iron Man | Automations, scripts, lovelace, input helpers (structural) |
| Black Widow | Device integrations, Z-Wave, Zigbee, MQTT, Docker/infra |
| Doctor Strange | Jinja2 templates, template sensors, helper logic |
| Hawkeye | Debugging, log analysis, entity ID research, diagnostics |
| Vision | AI/ML integrations, emerging tech, team training, prompt engineering |
| Scribe | Session logging, decision merging, `.squad/` git commits |
| Ralph | Work queue monitoring and escalation |

