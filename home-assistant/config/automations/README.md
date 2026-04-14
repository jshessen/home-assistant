# Automations Directory

This directory contains organized automation files that are automatically included by `automations.yaml` via:

```yaml
!include_dir_merge_list automations/
```

## Current Files

- **mode_management.yaml** - Good Night and Good Morning time-based automations
- **holiday_schedules.yaml** - Holiday decoration schedule automations

## Adding New Automations

You can add new automation files here with any name (e.g., `lighting.yaml`, `security.yaml`, etc.).

Each file should contain a YAML list of automations starting with `- id:`:

```yaml
- id: my_automation_1
  alias: "My Automation"
  description: What this does
  triggers:
    - trigger: state
      entity_id: input_boolean.something
  actions:
    - service: light.turn_on
      target:
        entity_id: light.living_room

- id: my_automation_2
  alias: "Another Automation"
  # ... etc
```

All `.yaml` files in this directory are automatically merged into the main automation list.
