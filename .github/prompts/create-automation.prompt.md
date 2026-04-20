---
mode: "agent"
tools: ["read_file", "create_file", "run_in_terminal"]
description: "Scaffold a new Home Assistant automation in automations/ directory"
---

Help the user create a new Home Assistant automation.

## Step 1: Gather requirements

Ask the user to describe the automation. You need:

- **Trigger:** What event starts this automation? (e.g., time, state change, sun event, device action)
- **Condition (optional):** Any conditions that must be true for the automation to run?
- **Action:** What should happen? (e.g., turn on a light, send a notification, run a script)
- **Name:** A short descriptive name for the automation

If any of these are unclear, ask before proceeding.

## Step 2: Read existing automations for style reference

Read one or two existing files from `home-assistant/config/automations/` to match the project's YAML style and structure.

## Step 3: Create the automation file

- Create a new `.yaml` file in `home-assistant/config/automations/`
- Name the file after the automation (e.g., `kitchen_lights_at_sunset.yaml`)
- Use **HA 2024.8+ syntax**: use `action:` not `service:` for actions
- Include a meaningful `id:` (snake_case, unique), `alias:`, and `description:`
- Follow this structure:

```yaml
- id: "unique_snake_case_id"
  alias: Human Readable Name
  description: "What this automation does"
  trigger:
    - ...
  condition:
    - ...
  action:
    - ...
  mode: single
```

**Do NOT add automations to `automations.yaml`** — that file uses `!include_dir_merge_list automations/` to auto-include all files in the directory.

## Step 4: Validate configuration

Run the config check:

```
timeout 30 docker exec home-assistant python -m homeassistant --script check_config -c /config 2>&1
```

Report any errors. If the config is valid, proceed to Step 5.

## Step 5: Remind how to reload

Tell the user:

> To activate the new automation **without a full restart**, go to:
> **Developer Tools → YAML → Reload Automations**
>
> A full restart is not needed for automation changes.
