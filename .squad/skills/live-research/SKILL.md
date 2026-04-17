# Skill: Live Research Protocol

**Confidence:** medium  
**Owner:** Yen (maintained), applicable to all members  
**Domain:** Any rapidly-evolving technical specification

---

## When to Apply

Apply this skill **before producing any implementation work** in a domain whose specifications change on a 30–90 day cycle. If you are about to write YAML, config, or code that depends on an external specification, ask: "could this have changed in the last release?" If yes, fetch the source first.

**Always fetch:** Z-Wave JS API, HA automation/script/template syntax, Zigbee2MQTT config schema, Mosquitto config, VS Code/Copilot agent capabilities, Ollama API.

**Safe to skip fetch:** Jinja2 core language syntax, Docker Compose v3 base spec, Python standard library, git commands.

---

## Protocol

### Step 1 — Identify required sources

Check your charter for a `## Live Research Requirements` section. If your charter has one, use the source table there.

If your charter does NOT have a `## Live Research Requirements` section (or the domain isn't listed), use the **Domain → Source Quick Reference** table at the bottom of this skill directly. Do not escalate — pick the closest matching domain and fetch it.

### Step 2 — Fetch current documentation

Use `fetch_webpage` to retrieve the relevant source URL. Target the most specific page (e.g., the triggers reference page, not the HA homepage). If the page has a "What's new" or changelog section, read it first.

```
fetch_webpage(url="https://www.home-assistant.io/docs/automation/trigger/",
              query="trigger syntax current release")
```

### Step 3 — Label your confidence

After reviewing the fetched source, label every non-trivial claim before implementation:

| Label                   | Meaning                                       | Action                           |
| ----------------------- | --------------------------------------------- | -------------------------------- |
| 🟢 Verified live        | Confirmed against fetched source              | Proceed                          |
| 🟡 Reasonable inference | Consistent with source, not explicitly stated | Proceed with note                |
| 🔴 Speculative          | Not found in fetched source                   | **Stop — flag for human review** |

### Step 4 — Document the source

When writing a decision to `.squad/decisions/inbox/`, include the source URL and fetch date so the team knows where the information came from.

```markdown
**Source:** https://www.home-assistant.io/docs/automation/trigger/ (fetched 2026-04-17)
**Confidence:** 🟢 Verified live
```

### Step 5 — Fallback when offline

If `fetch_webpage` fails or web access is unavailable:

1. State explicitly: **"training-data-only — web access unavailable"**
2. Label the entire output as 🔴 Speculative
3. Flag the output for human review before applying to production config
4. Write a note to `.squad/decisions/inbox/{your-name}-web-access-unavailable.md` so the team knows a fetch was needed

---

## Domain → Source Quick Reference

| Domain                  | Primary Source                                                 | Release Notes                                      |
| ----------------------- | -------------------------------------------------------------- | -------------------------------------------------- |
| Z-Wave JS API           | `https://zwave-js.github.io/node-zwave-js/`                    | `https://github.com/zwave-js/zwave-js-ui/releases` |
| HA automation syntax    | `https://www.home-assistant.io/docs/automation/`               | `https://www.home-assistant.io/blog/`              |
| HA script/action syntax | `https://www.home-assistant.io/docs/scripts/`                  | `https://www.home-assistant.io/blog/`              |
| HA Jinja2 templates     | `https://www.home-assistant.io/docs/configuration/templating/` | `https://developers.home-assistant.io/blog/`       |
| HA template integration | `https://www.home-assistant.io/integrations/template/`         | —                                                  |
| Zigbee2MQTT config      | `https://www.zigbee2mqtt.io/guide/configuration/`              | `https://github.com/Koenkk/zigbee2mqtt/releases`   |
| Mosquitto MQTT          | `https://mosquitto.org/documentation/`                         | `https://mosquitto.org/blog/`                      |
| Ollama API              | `https://github.com/ollama/ollama/blob/main/docs/api.md`       | `https://github.com/ollama/ollama/releases`        |
| VS Code Copilot agents  | `https://code.visualstudio.com/updates/`                       | `https://github.blog/tag/github-copilot/`          |
| HA HACS integrations    | Upstream GitHub repo README                                    | Upstream releases page                             |

---

## Anti-Patterns to Avoid

- Writing Z-Wave JS value IDs or commandClass names from memory — **fetch the current schema**
- Using HA service call syntax without checking if `action:` keyword applies — **fetch the action docs**
- Configuring Zigbee2MQTT device exposes from memory — **fetch the current device page**
- Claiming a HA feature exists based on training data — **verify it exists in the current release**
- Producing implementation and noting "this was accurate as of my training data" — **that is not acceptable; fetch or flag as 🔴**
