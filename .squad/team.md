# Squad Team

> home-assistant

## Coordinator

| Name  | Role        | Notes                                              |
| ----- | ----------- | -------------------------------------------------- |
| Squad | Coordinator | Routes work, enforces handoffs and reviewer gates. |

## Members

| Name            | Role                          | Charter                                      | Status    |
| --------------- | ----------------------------- | -------------------------------------------- | --------- |
| Nick Fury       | Lead                          | `.squad/agents/nick-fury/charter.md`         | ✅ Active  |
| Iron Man        | Automation Engineer           | `.squad/agents/iron-man/charter.md`          | ✅ Active  |
| Black Widow     | Integration Specialist        | `.squad/agents/black-widow/charter.md`       | ✅ Active  |
| Doctor Strange  | Template Dev                  | `.squad/agents/doctor-strange/charter.md`    | ✅ Active  |
| Hawkeye         | Troubleshooter                | `.squad/agents/hawkeye/charter.md`           | ✅ Active  |
| Captain America | Project Steward               | `.squad/agents/captain-america/charter.md`   | ✅ Active  |
| Vision          | AI & Emerging Tech Specialist | `.squad/agents/vision/charter.md`            | ✅ Active  |
| @copilot        | 🤖 Coding Agent               | `.github/copilot-instructions.md`            | 🤖 Async   |
| Scribe          | Session Logger                | `.squad/agents/scribe/charter.md`            | 📋 Silent  |
| Ralph           | Work Monitor                  | `.squad/agents/ralph/charter.md`             | 🔄 Monitor |

## Stewardship Ownership

- **Git Hygiene & Repo Stewardship Owner:** Captain America
- **Ownership Scope:** branch hygiene, repo cleanup checklists, release changelog and tagging workflow, `.gitignore`/`.gitattributes` boundaries, and GitHub issue/PR process hygiene

## @copilot Capability Profile

| Task Type | Suitability | Notes |
|-----------|-------------|-------|
| Dependency updates | 🟢 | Routine, mechanical, well-scoped |
| Test scaffolding | 🟢 | Known patterns, low judgment needed |
| Doc generation | 🟢 | Reads code, outputs markdown |
| Automation scaffolding (simple) | 🟡 | Needs clear spec; verify YAML output |
| Jinja2 template logic | 🔴 | Requires HA-specific context + Basher review |
| Architecture decisions | 🔴 | Always route to Danny |
| Z-Wave/Zigbee config | 🔴 | Always route to Linus |

<!-- copilot-auto-assign: false -->

## Project Context

- **Project:** home-assistant
- **Created:** 2026-04-14
