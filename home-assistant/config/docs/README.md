# Home Assistant Custom Documentation

This directory contains **custom documentation** created for your specific Home Assistant configuration. These files are separate from upstream/source project documentation to make it easy to identify your customizations.

## Directory Structure

```tree
docs/
├── README.md              # This file
├── alexa/                 # Alexa Smart Home integration documentation
├── holidays/              # Holiday automation and calendar documentation
├── keymaster/             # Keymaster lock code management documentation
├── modes/                 # House mode system documentation
└── setup/                 # Installation and configuration guides
```

## Documentation by Topic

### ⚡ Energy Cost Tracking (`docs/energy/ameren/`)

- **Ameren_IMPLEMENTATION_SUMMARY.md** - Complete implementation overview and status
- **Ameren_QUICK_START.md** - 5-minute setup guide for new users
- **Ameren_cost_tracking.md** - Complete guide to electricity and utility cost tracking
- **Ameren_PACKAGE_README.md** - Package and script details
- **Ameren_QUICK_REFERENCE.md** - Daily usage reference for rate manager

The energy cost tracking system uses:

- `utility_meter.yaml` - Consumption meters for daily/monthly cycles
- `input_number.yaml` - Adjustable seasonal rate helpers (Summer/Winter)
- `templates/energy_costs.yaml` - Template sensors for cost calculations with auto-switching
- `packages/ameren/` - Automated rate management assets
  - **ameren_rate_manager.py** - PDF parser and rate extraction script
  - **parsed_rates.json** - Cached parsed rates
- `packages/ameren.yaml` - Monthly automation and shell_command integration

### 🎄 Holiday Automation (`docs/holidays/`)

- **HOLIDAY_CALENDAR_REFERENCE.md** - Complete holiday calendar with date ranges and calculations
- **HOLIDAY_MANAGEMENT_PHASE1_COMPLETE.md** - Implementation notes and testing guide

The holiday system uses `input_select.active_holiday` which is automatically maintained by the `holiday_season_controller` automation.

### 🗣️ Alexa Integration (`docs/alexa/`)

- **ALEXA_QUICK_REFERENCE.md** - Quick reference for Alexa smart home setup
- **ALEXA_ORPHAN_CLEANUP_GUIDE.md** - Guide for cleaning up orphaned Alexa entities

Alexa configuration files are in the main config:

- `alexa.yaml` - Main Alexa configuration
- `alexa/include/` - Entities to expose to Alexa
- `alexa/exclude/` - Entities to hide from Alexa

### 🔐 Keymaster Lock Management (`docs/keymaster/`)

- **PR_SUBMISSION_GUIDE.md** - How to submit pull requests to keymaster upstream
- **PR_DESCRIPTION.md** - GitHub PR description for parent-child sync fix
- **PR_FIX_SYNC_LOOP.md** - Technical documentation of sync loop fix
- **PR_FIX_SYNC_LOOP.patch** - Git patch file for the fix

Keymaster integration files:

- `custom_components/keymaster/` - Integration code (v0.1.1-b1 with custom fixes)
- Lock-specific scripts in `scripts/keymaster_*_manual_notify.yaml`

### 🏠 House Mode System (`docs/modes/`)

- **MODE_AUTOMATION_README.md** - Complete house mode system documentation

Modes configuration:

- `input_select.house_mode` - Primary modes (Home/Away/Vacation/Guest)
- `input_boolean.night_mode` - Night mode toggle
- `scripts/good_night.yaml` - Evening automation
- `scripts/good_morning.yaml` - Morning automation

### 📦 Setup & Configuration (`docs/setup/`)

- **QUICK_START.md** - 5-minute quick start guide
- **SETUP_INSTRUCTIONS.md** - Complete deployment instructions
- **CONFIGURATION_CHECKLIST.md** - Step-by-step customization checklist
- **IMPLEMENTATION_SUMMARY.md** - What's built and next steps
- **LINTER_CONFIGURATION.md** - How ha-core is excluded from linters while maintaining imports
- **PYTHON_313_SETUP.md** - Python 3.13 installation and configuration guide

## Data Directory

Runtime data and logs are stored in `/config/data/` instead of mixed with scripts or configuration:

```tree
data/
├── alexa/                 # Alexa-related data files (HAR exports, logs, etc.)
└── [other services]/      # Additional service data as needed
```

This keeps your configuration clean and separates:

- **Config** (`/config/`) - YAML configuration files
- **Docs** (`/config/docs/`) - Custom documentation
- **Data** (`/config/data/`) - Runtime files, logs, caches
- **Scripts** (`/config/scripts/`) - HA script definitions only

## Distinguishing Source vs. Custom Files

### Source/Upstream Files

These come with Home Assistant or integrations:

- Hidden `.storage/` files (don't edit manually)
- `custom_components/*/` README files
- Integration-specific documentation in component folders

### Custom Files (This Directory)

All documentation in `docs/` is your custom work:

- Created as part of your configuration
- Safe to edit, update, or remove
- Not affected by Home Assistant updates
- Should be version controlled in your git repo

## Updating Documentation

When adding new features:

1. Create documentation in the appropriate `docs/` subdirectory
2. Update this README if adding a new category
3. Keep runtime data in `data/` not `scripts/` or config root
4. Use clear naming: `FEATURE_NAME_README.md` or `FEATURE_NAME_GUIDE.md`

## Quick Links

- Main Config: `/config/configuration.yaml`
- Automations: `/config/automations/`
- Scripts: `/config/scripts/`
- Templates: `/config/templates/`
- Custom Components: `/config/custom_components/`
