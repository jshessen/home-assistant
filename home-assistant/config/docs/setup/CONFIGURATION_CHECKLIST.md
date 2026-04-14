# 📋 Configuration Checklist

Use this file to track your progress customizing the automation system.

---

## Phase 1: Installation & Verification ✅

- [ ] All files created successfully
- [ ] Configuration check passes (`ha core check`)
- [ ] Home Assistant restarted
- [ ] No errors in logs (Settings > System > Logs)
- [ ] Helpers visible (Settings > Devices & Services > Helpers)
  - [ ] House Mode (input_select)
  - [ ] Active Holiday (input_select)
  - [ ] Night Mode (input_boolean)
  - [ ] Movie Mode (input_boolean)
  - [ ] Party Mode (input_boolean)
  - [ ] Holiday Decorations Inside (input_boolean)
  - [ ] Holiday Decorations Outside (input_boolean)
  - [ ] Disable Good Morning (input_boolean)
  - [ ] Disable Good Night (input_boolean)
  - [ ] Disable Holiday Schedules (input_boolean)

---

## Phase 2: Device Discovery 🔍

- [ ] Run Device Inventory script
  - Developer Tools > Services
  - Service: `script.device_inventory`
  - Click "Call Service"
- [ ] Check notifications for device lists
  - [ ] Locks list reviewed
  - [ ] Covers (garage/blinds) list reviewed
  - [ ] Lights list reviewed
  - [ ] Switches list reviewed
  - [ ] Fans list reviewed
  - [ ] Media Players (TVs/Alexa) list reviewed
  - [ ] Climate (thermostats) list reviewed
- [ ] Entity IDs copied for later use

---

## Phase 3: Good Night Script Configuration 🌙

File: `scripts/good_night.yaml`

### Door Locks
- [ ] Front door lock entity updated
  - Current: `lock.touchscreen_deadbolt_front_door` ✅
- [ ] Back door lock entity added (if applicable)
  - Entity: `lock._________________`
- [ ] Other locks added
  - Entity: `lock._________________`

### Garage Doors
- [ ] Main garage door entity added
  - Entity: `cover._________________`
- [ ] Additional garage doors (if applicable)
  - Entity: `cover._________________`

### Blinds/Shades
- [ ] Living room blinds
  - Entity: `cover._________________`
- [ ] Kitchen blinds
  - Entity: `cover._________________`
- [ ] Master bedroom blinds
  - Entity: `cover._________________`
- [ ] Guest room blinds
  - Entity: `cover._________________`
- [ ] Kids' room 1 blinds
  - Entity: `cover._________________`
- [ ] Kids' room 2 blinds
  - Entity: `cover._________________`
- [ ] Other blinds/shades
  - Entity: `cover._________________`

### TVs / Media Players
- [ ] Living room TV
  - Entity: `media_player._________________`
- [ ] Master bedroom TV
  - Entity: `media_player._________________`
- [ ] Kids' room 1 TV
  - Entity: `media_player._________________`
- [ ] Kids' room 2 TV
  - Entity: `media_player._________________`
- [ ] Other TVs
  - Entity: `media_player._________________`

### Lights by Room
- [ ] **Living Room**
  - Entity: `light._________________`
  - Entity: `light._________________`
- [ ] **Kitchen**
  - Entity: `light._________________`
  - Entity: `light._________________`
- [ ] **Dining Room**
  - Entity: `light._________________`
- [ ] **Hallway**
  - Entity: `light._________________`
- [ ] **Master Bedroom**
  - Overhead: `light._________________`
  - Lamps: `light.bedroom_lamps` ✅
- [ ] **Guest Room/Office**
  - Entity: `light._________________`
- [ ] **Kids' Room 1**
  - Entity: `light._________________`
- [ ] **Kids' Room 2**
  - Entity: `light._________________`

### Fans
- [ ] Bedroom fan
  - Entity: `fan._________________`
- [ ] Other fans
  - Entity: `fan._________________`

### Alexa Announcements
- [ ] Living room Echo
  - Entity: `media_player._________________`
- [ ] Bedroom Echo
  - Entity: `media_player._________________`

### Testing
- [ ] Good Night script tested manually
- [ ] All devices respond correctly
- [ ] Guest room skip works (when Guest mode active)
- [ ] Holiday decorations turn off
- [ ] Night mode enables

---

## Phase 4: Good Morning Script Configuration ☀️

File: `scripts/good_morning.yaml`

### Kitchen Lights
- [ ] Main kitchen lights
  - Entity: `light._________________`
- [ ] Under cabinet lights
  - Entity: `light._________________`
- [ ] Other kitchen lights
  - Entity: `light._________________`

### Blinds (if different from Good Night)
- [ ] Main living area blinds
  - Entity: `cover._________________`
  - Entity: `cover._________________`
- [ ] Bedroom blinds
  - Entity: `cover._________________`

### Kids' Room Lights (for school mornings)
- [ ] Kid room 1
  - Entity: `light._________________`
- [ ] Kid room 2
  - Entity: `light._________________`

### Alexa Announcements
- [ ] Kitchen Echo
  - Entity: `media_player._________________`

### Testing
- [ ] Good Morning script tested manually
- [ ] Weekday behavior tested
- [ ] Weekend behavior tested
- [ ] Kitchen lights turn on correctly
- [ ] Blinds open gradually
- [ ] Kids' lights activate (weekdays only)

---

## Phase 5: Holiday Switch Configuration 🎄

File: `templates/holiday_switches.yaml`

### Halloween
- [ ] Outside decorations/inflatables
  - Current entity: `switch.halloween_outside`
  - Update to: `switch._________________`
- [ ] Inside decorations
  - Update to: `switch._________________`

### Thanksgiving
- [ ] Turkey Tom (inflatable)
  - Current entity: `switch.thanksgiving_inflatable`
  - Update to: `switch._________________`
- [ ] Other decorations
  - Update to: `switch._________________`

### Christmas
- [ ] Tree inside
  - Current entity: `switch.christmas_tree_inside`
  - Update to: `switch._________________`
- [ ] Lights outside
  - Current entity: `switch.christmas_lights_outside`
  - Update to: `switch._________________`
- [ ] All Christmas (group)
  - Current entity: `switch.christmas_all`
  - Update to: `switch._________________`

### Easter
- [ ] Inflatable/decorations
  - Current entity: `switch.easter_inflatable`
  - Update to: `switch._________________`

### July 4th
- [ ] Patriotic lights
  - Current entity: `switch.july4th_lights`
  - Update to: `switch._________________`

### Testing
- [ ] Set Active Holiday to Halloween
- [ ] Turn on "Pumpkin Patch" - verify it works
- [ ] Set Active Holiday to Christmas
- [ ] Turn on "Christmas Spirit" - verify it works
- [ ] Test each holiday switch

---

## Phase 6: Schedule Customization ⏰

File: `packages/mode_automations.yaml`

### Good Night Times
- [ ] Weekday time adjusted
  - Current: 23:00:00 (11 PM)
  - Desired: `__:__:__`
- [ ] Weekend time adjusted
  - Current: 00:00:00 (Midnight)
  - Desired: `__:__:__`

### Good Morning Times
- [ ] Weekday time adjusted
  - Current: 06:00:00 (6 AM)
  - Desired: `__:__:__`
- [ ] Weekend time adjusted
  - Current: 08:00:00 (8 AM)
  - Desired: `__:__:__`

File: `packages/holiday_automations.yaml`

### Holiday Decoration Times
- [ ] Inside decorations ON time
  - Current: 06:00:00 (6 AM)
  - Desired: `__:__:__`
- [ ] Outside decorations ON time (weekday)
  - Current: 15:00:00 (3 PM)
  - Desired: `__:__:__`
- [ ] Outside decorations ON time (weekend)
  - Current: 10:00:00 (10 AM)
  - Desired: `__:__:__`
- [ ] Decorations OFF time
  - Current: 23:00:00 (11 PM)
  - Desired: `__:__:__`

---

## Phase 7: Alexa Integration 🎙️

### Device Discovery
- [ ] Alexa app opened
- [ ] Devices > + > Add Device > Other
- [ ] Discovery completed
- [ ] New entities appear in Alexa app

### Alexa Routines Created

#### Core Routines
- [ ] **"Alexa, good night"**
  - Action: Turn on input_boolean.night_mode
- [ ] **"Alexa, good morning"**
  - Action: Run script.good_morning
- [ ] **"Alexa, movie time"**
  - Action: Turn on input_boolean.movie_mode
- [ ] **"Alexa, party mode"**
  - Action: Turn on input_boolean.party_mode

#### House Mode Routines
- [ ] **"Alexa, we're home"**
  - Action: Set input_select.house_mode to "Home"
- [ ] **"Alexa, we're leaving"**
  - Action: Set input_select.house_mode to "Away"

#### Holiday Decoration Routines
- [ ] **"Alexa, turn on Turkey Tom"**
  - Action: Turn on switch.turkey_tom
- [ ] **"Alexa, turn on Pumpkin Patch"**
  - Action: Turn on switch.pumpkin_patch
- [ ] **"Alexa, turn on Christmas Spirit"**
  - Action: Turn on switch.christmas_spirit
- [ ] **"Alexa, turn on the Christmas tree"**
  - Action: Turn on switch.christmas_tree_inside

### Voice Command Testing
- [ ] "Alexa, good night" works
- [ ] "Alexa, good morning" works
- [ ] "Alexa, movie time" works
- [ ] "Alexa, turn on Turkey Tom" works
- [ ] "Alexa, turn on Pumpkin Patch" works
- [ ] "Alexa, turn on Christmas Spirit" works

---

## Phase 8: Dashboard Configuration 📱

File: `lovelace/mode_dashboard.yaml`

- [ ] New dashboard view created
- [ ] Mode Control card added
- [ ] Holiday Control card added
- [ ] Quick Actions grid added
- [ ] Status Glance card added
- [ ] Dashboard tested
- [ ] All buttons work correctly
- [ ] Conditional holiday cards appear

---

## Phase 9: Testing & Validation ✅

### Manual Script Testing
- [ ] Good Night script runs completely
- [ ] Good Morning script runs completely
- [ ] Device Inventory script works
- [ ] All devices respond as expected

### Automation Testing
- [ ] Good Night automation triggers at scheduled time
- [ ] Good Morning automation triggers at scheduled time
- [ ] Holiday schedules trigger correctly
- [ ] Mode changes trigger behaviors
- [ ] Away → Vacation switch works (24 hour test)
- [ ] Party mode auto-disables after 6 hours
- [ ] Guest mode skip works in Good Night

### Edge Case Testing
- [ ] Good Night with Guest mode active
- [ ] Good Night with Party mode active
- [ ] Good Morning on Vacation mode (should skip)
- [ ] Holiday switches when wrong holiday active
- [ ] Manual disable flags work
- [ ] Multiple mode changes in short time

---

## Phase 10: Fine-Tuning 🎯

### Adjustments Made
- [ ] Light brightness levels adjusted
- [ ] Timing delays adjusted
- [ ] Room behaviors customized
- [ ] Holiday schedules tweaked
- [ ] Notification messages customized
- [ ] Alexa announcement text adjusted

### Additional Features Added
- [ ] Coffee maker automation
- [ ] Thermostat adjustments
- [ ] Additional holidays
- [ ] Additional rooms
- [ ] Custom conditions
- [ ] Additional voice commands

---

## Final Verification ✨

- [ ] System running smoothly for 7 days
- [ ] No unexpected behaviors
- [ ] Family members can use it easily
- [ ] Voice commands reliable
- [ ] Schedules work correctly
- [ ] Holiday transitions smooth
- [ ] Guest mode tested with actual guests
- [ ] Party mode tested with actual party
- [ ] Vacation mode tested (or simulated)
- [ ] All documentation updated with customizations

---

## 🎉 Success!

When all checkboxes are complete, you have successfully:
- ✅ Migrated SmartThings functionality to Home Assistant
- ✅ Enhanced with new capabilities
- ✅ Integrated voice control
- ✅ Automated holiday management
- ✅ Created a robust, flexible home automation system

---

## Notes & Customizations

Use this space to document your specific customizations:

```
[Your notes here]




```

---

**Date Started**: _________________
**Date Completed**: _________________
**Hours Spent**: _________________

**Happy Automating! 🏠✨**
