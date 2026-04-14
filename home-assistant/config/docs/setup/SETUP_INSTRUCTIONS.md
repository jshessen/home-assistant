# ============================================================================
# Quick Setup Instructions - Mode & Holiday Automations
# ============================================================================

## Current Status

✅ **Working:**
- All helper entities (input_select, input_boolean) are configured
- Good Night and Good Morning scripts are ready
- Holiday template switches are defined
- Alexa integration is configured
- Dashboard is ready to add

❌ **Not Yet Active:**
- Automations are NOT loaded (removed due to YAML package errors)
- Scripts need your actual device entity IDs

## Next Steps (Choose ONE)

### Option 1: Already Done! (EASIEST)

The automations are already in the `automations/` directory and will be automatically loaded:
- `automations/mode_management.yaml` - Good Night/Morning schedules
- `automations/holiday_schedules.yaml` - Holiday decoration schedules

The `automations.yaml` file includes these via `!include_dir_merge_list automations/` at the bottom.

**Just restart Home Assistant to load them!**

### Option 2: Use Home Assistant UI (IF YOU WANT TO CUSTOMIZE)

1. Go to Settings > Automations & Scenes
2. Click "+ Create Automation"
3. Click "⋮" menu > "Edit in YAML"
4. Copy one automation at a time from `automations/mode_management.yaml` or `automations/holiday_schedules.yaml`
5. Save each one individually

### Option 3: Add More Automation Files (ADVANCED)

To add your own automation files:
1. Create new YAML file in `automations/` directory (e.g., `automations/my_automations.yaml`)
2. Add automation list (starting with `- id: ...`)
3. They'll be automatically included via the `!include_dir_merge_list automations/` directive in `automations.yaml`

## Update Device Entity IDs

Before automations will work, you must update entity IDs in:

1. **scripts/good_night.yaml** - Search for "TODO" comments:
   - Lock entities (front/back doors)
   - Cover entities (garage, blinds)
   - Light groups
   - Media players
   - Fan entity

2. **scripts/good_morning.yaml** - Search for "TODO" comments:
   - Cover entities
   - Light entities
   - Media player for kids' room

3. **templates/holiday_switches.yaml** - Map to actual outlets:
   - `switch.pumpkin_patch` → Your Halloween outlet switch
   - `switch.turkey_tom` → Your Thanksgiving outlet switch
   - `switch.christmas_spirit` → Your Christmas outlet switch

### To Find Your Entity IDs:

Run the device inventory script:
1. Go to Developer Tools > Services
2. Call `script.device_inventory`
3. Check `device_inventory.txt` in your config folder
4. Find entity IDs for your locks, switches, covers, lights, etc.

## Testing

After loading automations and updating entity IDs:

1. **Manual Test:**
   - Developer Tools > Services
   - Call `script.good_night`
   - Verify it locks doors, closes things, turns off lights

2. **Check Configuration:**
   - Settings > System > Restart
   - Click "Check Configuration" first
   - Fix any errors before restarting

3. **Voice Control:**
   - Open Alexa app
   - Go to Devices > Discover Devices
   - Wait for discovery to complete
   - Create routines:
     - "Alexa, good night" → Turn on `input_boolean.night_mode`
     - "Alexa, turn on Turkey Tom" → Turn on `switch.turkey_tom`

## Dashboard

Add the mode dashboard:
1. Settings > Dashboards
2. Edit your dashboard
3. Add new view
4. Click "⋮" > "Raw configuration editor"
5. Paste content from `lovelace/mode_dashboard.yaml`

## Troubleshooting

**"Entity not found" errors:**
- Update TODO placeholders with your actual entity IDs
- Run `script.device_inventory` to find correct IDs

**"Unknown error occurred":**
- Check Developer Tools > Logs for specific error
- Verify YAML indentation (use spaces, not tabs)

**Automations not triggering:**
- Check conditions are met (e.g., night_mode is on, disable flags are off)
- Look at automation traces: Settings > Automations > Click automation > ⋮ > Traces

**Voice commands not working:**
- Verify entities are exposed in `alexa.yaml`
- Rediscover devices in Alexa app
- Check Alexa app logs for integration errors

## Files Reference

- `automations/mode_management.yaml` - Time-based Good Night/Morning automations
- `automations/holiday_schedules.yaml` - Holiday decoration schedule automations
- `automations.yaml` - Main automation file (includes automations/ directory)
- `input_select.yaml` - House mode and holiday selector
- `input_boolean.yaml` - Night/Movie/Party toggles and disable flags
- `scripts/good_night.yaml` - Comprehensive shutdown routine
- `scripts/good_morning.yaml` - Wake-up routine with weekday/weekend logic
- `templates/holiday_switches.yaml` - Voice-friendly holiday switches
- `automations_mode_management_template.yaml` - Time-based automation templates
- `automations_holiday_template.yaml` - Holiday schedule automation templates
- `alexa.yaml` - Entity exposure configuration
- `lovelace/mode_dashboard.yaml` - Dashboard UI

## Support

For detailed documentation, see:
- `MODE_AUTOMATION_README.md` - Complete system overview
- `CONFIGURATION_CHECKLIST.md` - Step-by-step setup guide
- `IMPLEMENTATION_SUMMARY.md` - Feature summary

============================================================================
