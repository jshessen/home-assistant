# Livingston — History

## Core Context

- **Project:** A full-featured Home Assistant environment with smart automations, device integrations, custom templates, and ongoing troubleshooting support.
- **Role:** Troubleshooter
- **Joined:** 2026-04-14T17:06:50.078Z

## Learnings

### 2026-04-14: Entity IDs resolved: kitchen lights = light.kitchen_light_3, guest desk lamp = light.guest_outlet_3, persons = person.jeff + person.patricia

Resolved 3 previously TBD entity IDs from entity registry scan. Kitchen cabinet lights map to `light.kitchen_light_3` (only active kitchen light entity; no dedicated under-cabinet entity exists — use at ~10% brightness for pre-dawn). Guest desk lamp maps to `light.guest_outlet_3` (switch_as_x wrapper, not the raw switch entities). Full person entity list confirmed as `person.jeff` and `person.patricia` only. Also identified `light.bedroom_lamps` (main bedroom group) and `light.bedroom_lamps_2` (kids bedroom). No office light entity exists in current registry. Decision filed: `decisions.md`.
