# Home Assistant Docker Setup - AI Coding Agent Instructions

## Project Architecture

This is a **multi-service Home Assistant deployment** using Docker Compose with modular YAML includes. The repository has a multi-root VS Code workspace (`home-assistant.code-workspace`) with 4 distinct areas:

1. **Home Assistant Config** (`home-assistant/config/`) - Main HA configuration with extensive YAML includes
2. **External Connectors** (`home-assistant/ha-external-connector/`) - Placeholder infrastructure for external integrations
3. **Cloudflare Workers** (`home-assistant/cloudflare/`) - Authentik auth proxy for external access
4. **Root** (`.`) - Docker Compose orchestration and Makefile commands

## Critical Configuration Pattern: YAML Includes

Home Assistant config uses **extensive YAML includes** - never duplicate content that's being included:

```yaml
# configuration.yaml includes from multiple locations:
automation: !include_dir_merge_list automations/     # Merges all YAML files in automations/
script: !include_dir_merge_named scripts/            # Each file becomes a named script
template: !include_dir_merge_list templates/         # Merges template lists
packages: !include_dir_named packages/               # Each package file is a complete HA config subset
```

**When modifying configs:**

- Check `configuration.yaml` first to see what's included from where
- Edit files in their included locations (e.g., scripts in `scripts/`, not inline)
- Automations go in `automations/` directory as separate files, NOT in `automations.yaml`
- Templates go in `templates/` directory as separate YAML files

## Development Workflow

### Container Names Reference

The Docker Compose setup uses the following container names:

- `home-assistant` - Main Home Assistant container (note: hyphenated)
- `zwave-js-ui` - Z-Wave JS UI container
- `zigbee2mqtt` - Zigbee2MQTT container
- `mqtt` - Eclipse Mosquitto MQTT broker
- `homeassistant-postgres` - PostgreSQL database for recorder

**Important:** When running `docker exec` or `docker logs` commands, use `home-assistant` (with hyphen), not `homeassistant`.

### Building & Running Services

Use **Makefile targets** (not raw docker compose commands):

```bash
make hacs        # Start only Home Assistant + Z-Wave
make all         # Start all services (HA, MQTT, Zigbee, Z-Wave)
make restart     # Restart all running services
make down        # Stop all services
make update      # Pull latest images and restart
```

Compose files are modular:

- `docker-compose.yml` - Base Home Assistant (host network mode)
- `docker-compose.zwave.yml` - Z-Wave JS UI
- `docker-compose.zigbee.yml` - Zigbee2MQTT
- `docker-compose.mqtt.yml` - Eclipse Mosquitto
- `docker-compose.postgres.yml` - PostgreSQL for recorder

### Configuration Validation

**ALWAYS validate before restarting:**

```bash
# Using VS Code task (preferred)
Task: "Check Home Assistant Config"

# Or directly with docker
docker exec home-assistant python -m homeassistant --script check_config -c /config
```

### Restarting Home Assistant

```bash
# Using VS Code task
Task: "Restart Home Assistant"

# Or with Makefile
make restart

# Or with docker
docker restart home-assistant
```

## Custom Integrations & Components

Located in `custom_components/`:

- **keymaster** - Z-Wave lock code management (generates lovelace dashboards per lock)
- **hacs** - Home Assistant Community Store
- **spook** - Enhanced debugging/templating tools
- **alarmo**, **monitor_docker**, **presence_simulation** - Additional integrations

Keymaster generates lovelace files at `custom_components/keymaster/lovelace/*.yaml` - these are auto-generated, don't manually edit.

## Smart Home Device Patterns

### Entity Discovery Script

The project includes a device inventory script for discovering entities:

```yaml
# Developer Tools > Services > script.device_inventory
# Results appear in notifications with lists of locks, covers, lights, media_players, etc.
```

### Entity ID Conventions

Lock entities follow pattern: `lock.touchscreen_deadbolt_<location>`

- `lock.touchscreen_deadbolt_front_door`
- `lock.touchscreen_deadbolt_back_door`
- `lock.touchscreen_deadbolt_kitchen_entry`

Scripts and automations have extensive TODO comments where entity IDs need updating for specific deployments.

## Mode & Holiday Automation System

The project has a comprehensive house mode system:

**Input Helpers** (`input_select.yaml`, `input_boolean.yaml`):

- Primary modes: Home/Away/Vacation/Guest (mutually exclusive)
- Secondary toggles: Night Mode, Movie Mode, Party Mode
- Holiday system: Active Holiday selector + inside/outside decoration controls

**Scripts** (`scripts/`):

- `good_night.yaml` - Comprehensive shutdown routine (locks, covers, lights, TVs)
- `good_morning.yaml` - Morning wake routine (lights, blinds)
- `device_inventory.yaml` - Entity discovery helper

**Automations** (`automations/`):

- `mode_management.yaml` - Time-based Good Night/Morning triggers
- `holiday_schedules.yaml` - Seasonal decoration schedules

**Templates** (`templates/`):

- `holiday_switches.yaml` - Named voice-control switches (Turkey Tom, Pumpkin Patch, Christmas Spirit)
- `seasonal_displays.yaml` - Current active file being edited

## Alexa Integration

Smart Home skill configured in `alexa.yaml`:

- Filter approach: Include domains, then exclude unwanted entities
- Entities exposed via `alexa/include/` and `alexa/exclude/` directories
- Template sensors track connection status for external Lambda wrapper
- Client credentials in config (not secrets file)

Voice control requires:

1. Discovering devices in Alexa app after config changes
2. Creating Alexa routines that trigger `input_boolean` entities
3. Using template switches for holiday decorations with friendly names

## Database Configuration

Uses **PostgreSQL** instead of SQLite for performance:

- Connection: `recorder.yaml` with `db_url: postgresql://...` to localhost
- Home Assistant runs in host network mode, connects to containerized Postgres
- 30-second commit interval, 14-day retention
- Excludes noisy sensors (RSSI, uptime, last_seen patterns)

## Z-Wave & Zigbee

**Z-Wave JS UI** (`docker-compose.zwave.yml`):

- Device at `/dev/ttyACM0` (check actual device path if issues)
- Web UI on port 8091
- MQTT gateway mode for HA integration

**Zigbee2MQTT** (`docker-compose.zigbee.yml`):

- Web UI on port 8080
- USB device binding required (check compose file for device path)

Both use Home Automation bridge network (`172.16.2.0/27`), except HA which uses host mode.

## Security & Secrets

Secrets stored in `secrets/` directory as individual files:

- `mqtt_admin`, `mqtt_admin_password`
- `postgres_password`
- `zigbee2mqtt`, `zwave-js-ui`

These are mounted as Docker secrets (non-swarm mode - direct file mounts).

**DO NOT commit:**

- `secrets/` directory contents
- `.storage/` directory (Home Assistant internal storage)
- `*.log*` files
- `deps/` directory (Python dependencies cache)

## Blueprint System

Home Assistant blueprints are in `blueprints/`:

- Automations in `blueprints/automation/`
- Scripts in `blueprints/script/`
- Templates in `blueprints/template/`

Used via `use_blueprint:` in `automations.yaml`. Custom blueprints in `blueprints/automation/jshessen/` include Z-Wave dimmer controls.

## Cloudflare Worker (External Access)

`home-assistant/cloudflare/worker/authentik-proxy.js`:

- Minimal proxy for Authentik OAuth at `auth.hessenflow.net`
- Adds `X-Forwarded-*` headers without breaking OAuth flows
- Uses `redirect: 'manual'` to preserve backend redirect handling
- Deployed via Cloudflare Workers (no build step required)

## Lovelace Dashboards

Dashboard mode: `storage` with selective YAML includes:

- `lovelace.yaml` - Main dashboard config
- `lovelace/` directory contains per-feature dashboards:
  - `mode_dashboard.yaml` - House mode controls
  - `keymaster.yaml` - Dynamically includes lock dashboards from custom_component
  - Per-lock dashboards (auto-generated by keymaster)

Add new dashboard views in separate YAML files, reference in `lovelace.yaml`.

## Documentation Standards

**CRITICAL: All custom documentation goes in `/config/docs/` subdirectories, NOT in `/config/` root!**

Project uses organized documentation structure:

- **`/config/docs/alexa/`** - Alexa Smart Home integration guides
- **`/config/docs/holidays/`** - Holiday automation system documentation
- **`/config/docs/modes/`** - House mode system documentation
- **`/config/docs/setup/`** - Installation and configuration guides

See `/config/docs/README.md` for complete documentation index.

**When implementing new features:**

1. Create or update docs in appropriate `/config/docs/` subdirectory
2. Add entry to `/config/docs/README.md` index
3. NEVER create `.md` files directly in `/config/` root
4. Reference docs using relative paths: `docs/category/FILE.md`

**Files that belong in `/config/` root:**

- `configuration.yaml` and related YAML config files
- `automations.yaml`, `scenes.yaml`, etc.
- `.storage/` directory (HA managed)
- `.gitignore`, `.HA_VERSION` (system files)

**Everything else:**

- Documentation → `/config/docs/`
- Runtime data/logs → `/config/data/`
- Custom components → `/config/custom_components/`

## Package Pattern (Advanced Config Organization)

`packages/` directory for self-contained feature modules:

- `ios_companion.yaml` - iOS app integration with template sensors, input_datetime, counters
- Each package is a complete HA config subset with all needed entities

Package files can include: `template:`, `input_datetime:`, `counter:`, `automation:`, etc. - full YAML config scope.

## Troubleshooting & Logs

### Accessing Logs Efficiently

This is a **remote explorer session** - logs are available directly on the filesystem, not just through containers:

**Z-Wave JS UI logs:**

```bash
# Direct file access (faster than docker logs)
tail -f zwave/logs/z-ui_current.log
grep -i "error\|dead\|timeout" zwave/logs/z-ui_current.log

# Only use docker logs when container not writing to files
docker logs zwave-js-ui --tail 100
```

**Home Assistant logs:**

```bash
# Direct file access (faster than docker logs)
tail -f home-assistant/config/home-assistant.log
grep -i "error\|warning" home-assistant/config/home-assistant.log

# Only use docker logs when container not writing to files
docker logs home-assistant --tail 100
```

**Zigbee2MQTT logs:**

```bash
# Check compose file for log volume mount location
tail -f zigbee2mqtt/data/log/*.log
```

### Z-Wave Network Issues

**Common symptoms:**

- Command delays (5-10 seconds) across all Z-Wave devices
- Devices marked as "dead" in Z-Wave JS UI

**Quick diagnosis:**

```bash
# Check for dead nodes and errors
grep -i "dead\|error\|timeout" zwave/logs/z-ui_current.log | tail -50
```

**Common causes:**

1. **Low battery on battery-powered devices** - Check Z-Wave JS UI (port 8091) for battery levels below 40%
2. **Mesh network congestion** - Failed devices cause retry loops that block all commands
3. **USB interference** - Z-Wave stick on USB 3.0 port or near wireless devices

**Recovery steps:**

1. Restart Z-Wave JS UI: `docker restart zwave-js-ui`
2. Replace batteries in low-battery devices (especially locks)
3. Manually wake battery devices: Remove battery 10 seconds, reinsert
4. Network heal in Z-Wave JS UI: Settings → Network → Heal Network

## Common Pitfalls

1. **Don't add automations to `automations.yaml`** - add to `automations/` directory instead
2. **Don't create docs in `/config/` root** - use `/config/docs/` subdirectories (see Documentation Standards)
3. **Check host network implications** - HA container uses host networking, affects port bindings
4. **YAML custom tags** - VS Code workspace has custom tag support for `!include`, `!secret`, etc.
5. **Entity ID updates needed** - Many scripts have TODOs for site-specific entity IDs
6. **Validate before restart** - Always run config check task before restarting HA
7. **Use direct file access for logs** - Faster than `docker logs` in remote explorer sessions
