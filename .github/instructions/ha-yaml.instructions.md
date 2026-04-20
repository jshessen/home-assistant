---
applyTo: "**/*.yaml"
description: "Home Assistant YAML conventions for this project"
---

# Home Assistant YAML Conventions

## Include Directives (`configuration.yaml`)

- `!include <file>` — single file, any domain
- `!include_dir_merge_list <dir>/` — merges all YAML files as a list (automations, templates)
- `!include_dir_merge_named <dir>/` — merges all files as named keys (scripts)
- `!include_dir_named <dir>/` — each file becomes a top-level key (packages)
- `!secret <key>` — reads from `secrets.yaml`
- `!env_var <VAR>` — reads from environment (valid custom tag in this workspace)

## File Placement Rules

- **Automations** → `automations/` directory (separate `.yaml` files). **NOT** inline in `automations.yaml`
- **Scripts** → `scripts/` (each file is a named script)
- **Templates** → `templates/` (merged as list)
- **Packages** → `packages/` (self-contained feature modules with full config scope)
- **Lovelace views** → `lovelace/` (referenced from `lovelace.yaml`)

## HA 2024.8+ Syntax

- Use `action:` not `service:` for all service calls
- `target:` structure: `target: { entity_id: ... }` or multi-line block
- Condition keys: `condition:` block in automations; `conditions:` in `choose:` branches

## YAML Anchors (codebase pattern)

Anchors defined on first use, aliased everywhere else:

```yaml
sort: &battery-sort
  - by: state
tap_action: &battery-tap
  action: more-info
# Re-use:
sort: *battery-sort
tap_action: *battery-tap
```

- `&anchor-name` — defines anchor
- `*anchor-name` — references anchor
- `<<: *anchor-name` — merge anchor into current mapping
- Anchors are file-scoped (not cross-file)

## Entity ID Conventions

- Locks: `lock.touchscreen_deadbolt_<location>` (front_door, back_door, kitchen_entry)
- Battery sensors: `sensor.<device>_battery_plus` (Battery Notes integration)
- Battery low binary: `sensor.<device>_battery_plus_low` (exclude from most filters)
- Battery replaced buttons: `button.<device>_battery_replaced`
- Holiday mode: `input_select.active_holiday`

## Config Validation

**Always run before restarting:**

```bash
docker exec home-assistant python -m homeassistant --script check_config -c /config
```

Container name is `home-assistant` (hyphenated). Never `homeassistant`.

## Custom YAML Tags (valid in this workspace)

`!include`, `!include_dir_merge_list`, `!include_dir_merge_named`, `!include_dir_named`, `!secret`, `!env_var`
VS Code workspace has custom tag support — no linter errors for these.

## Restart

```bash
make restart         # preferred (Makefile target)
docker restart home-assistant
```
