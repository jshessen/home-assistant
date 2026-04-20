# Squad Team

> home-assistant

## Coordinator

| Name  | Role        | Notes                                              |
| ----- | ----------- | -------------------------------------------------- |
| Squad | Coordinator | Routes work, enforces handoffs and reviewer gates. |

## Members

| Name       | Role                          | Charter                               | Status    |
| ---------- | ----------------------------- | ------------------------------------- | --------- |
| Danny      | Lead                          | `.squad/agents/danny/charter.md`      | ✅ Active  |
| Rusty      | Automation Engineer           | `.squad/agents/rusty/charter.md`      | ✅ Active  |
| Linus      | Integration Specialist        | `.squad/agents/linus/charter.md`      | ✅ Active  |
| Basher     | Template Dev                  | `.squad/agents/basher/charter.md`     | ✅ Active  |
| Livingston | Troubleshooter                | `.squad/agents/livingston/charter.md` | ✅ Active  |
| Saul       | Project Steward               | `.squad/agents/saul/charter.md`       | ✅ Active  |
| Yen        | AI & Emerging Tech Specialist | `.squad/agents/yen/charter.md`        | ✅ Active  |
| @copilot   | 🤖 Coding Agent               | `.github/copilot-instructions.md`     | 🤖 Async   |
| Scribe     | Session Logger                | `.squad/agents/scribe/charter.md`     | 📋 Silent  |
| Ralph      | Work Monitor                  | `.squad/agents/ralph/charter.md`      | 🔄 Monitor |

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
