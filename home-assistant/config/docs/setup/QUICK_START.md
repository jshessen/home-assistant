# 🚀 Quick Start Guide - Mode Automation System

## ⚡ 5-Minute Setup

### Step 1: Check Configuration (1 min)
```bash
# Run configuration check
ha core check
```
OR use VS Code Task: "Check Home Assistant Config"

### Step 2: Restart Home Assistant (2 min)
```bash
# Restart
ha core restart
```
OR use VS Code Task: "Restart Home Assistant"

### Step 3: Discover Your Devices (1 min)

1. Go to **Developer Tools** > **Services**
2. Select service: `script.device_inventory`
3. Click **"Call Service"**
4. Check your **Notifications** (bell icon in sidebar)
5. You'll see lists of all your:
   - Locks
   - Garage doors & blinds
   - Lights
   - Switches/outlets
   - Fans
   - TVs & Alexa devices

### Step 4: Update Scripts (30 min - 1 hour)

Open these files and replace TODO items with your actual entity IDs:

1. **scripts/good_night.yaml**
   - Replace `lock.touchscreen_deadbolt_front_door` with your locks
   - Replace `cover.garage_door` with your garage
   - Replace light entities for each room
   - Replace `media_player.` entities for TVs
   - Replace `fan.` entity for bedroom fan
   - Replace Alexa devices for announcements

2. **scripts/good_morning.yaml**
   - Replace kitchen lights
   - Replace cover entities for blinds
   - Replace kids' room lights
   - Replace Alexa device

3. **templates/holiday_switches.yaml**
   - Replace `switch.halloween_outside` etc. with your actual holiday switches

### Step 5: Test! (5 min)

Go to **Developer Tools** > **Services**

Test each script:
- `script.good_night`
- `script.good_morning`
- `script.device_inventory`

---

## 🎯 What You Get Out of the Box

### ✅ Already Working (No Config Needed)

1. **House Modes**:
   - Home/Away/Vacation/Guest selector
   - Night/Movie/Party toggles
   - Automatic Away → Vacation after 24 hours

2. **Holiday System**:
   - Holiday selector (Halloween, Thanksgiving, Christmas, etc.)
   - Auto-switching based on dates
   - Inside/Outside decoration controls

3. **Automations**:
   - Good Night: Weekday 11 PM, Weekend Midnight
   - Good Morning: Weekday 6 AM, Weekend 8 AM
   - Holiday schedules (once you configure switches)
   - Mode change behaviors

### ⚙️ Needs Configuration (Use Your Entity IDs)

1. **Good Night Script** - Add your devices
2. **Good Morning Script** - Add your devices
3. **Holiday Switches** - Map to your outlets
4. **Alexa Announcements** - Add your Echo devices

---

## 🎙️ Voice Control Quick Setup

### In Alexa App

1. **Discover Devices**:
   - Devices > + > Add Device > Other
   - Wait 30-60 seconds

2. **Create Routines**:

**"Alexa, good night"**
```
When: You say "good night"
Alexa will: Control Device > Night Mode > Turn On
```

**"Alexa, good morning"**
```
When: You say "good morning"
Alexa will: Control Device > Good Morning > Run
```

**"Alexa, turn on Turkey Tom"**
```
When: You say "turn on Turkey Tom"
Alexa will: Control Device > Turkey Tom > Turn On
```

---

## 📱 Dashboard Quick Add

1. Go to your Home Assistant dashboard
2. Click "⋮" (top right) > "Edit Dashboard"
3. Click "+ Add Card"
4. Click "Show Code Editor" (bottom)
5. Copy/paste sections from: `lovelace/mode_dashboard.yaml`
6. Click "Save"

---

## 🔍 Quick Troubleshooting

### "Configuration invalid" error
→ Run `ha core check` to see specific error
→ Usually means a YAML indentation issue

### Scripts don't show up
→ Check `configuration.yaml` has: `script: !include_dir_merge_named scripts/`
→ Restart Home Assistant

### Holiday switches not appearing
→ Entity IDs in `templates/holiday_switches.yaml` must exist
→ Replace placeholder entities with real ones

### Alexa can't find devices
→ Make sure `alexa.yaml` includes the entities
→ Restart HA, then discover in Alexa app

---

## 📋 Configuration Checklist

Use this to track your progress:

### Phase 1: Foundation
- [ ] Configuration check passes
- [ ] Home Assistant restarted
- [ ] Helpers visible in Settings > Helpers
- [ ] Device inventory script run
- [ ] Entity IDs collected

### Phase 2: Core Scripts
- [ ] Good Night script - entity IDs updated
- [ ] Good Night script - tested manually
- [ ] Good Morning script - entity IDs updated
- [ ] Good Morning script - tested manually

### Phase 3: Holiday System
- [ ] Holiday switches - entity IDs updated
- [ ] Test one holiday switch (e.g., Christmas)
- [ ] Verify holiday automations enabled

### Phase 4: Voice Control
- [ ] Alexa discovery run
- [ ] "Good night" routine created
- [ ] "Good morning" routine created
- [ ] Holiday routines created
- [ ] All voice commands tested

### Phase 5: Polish
- [ ] Dashboard added
- [ ] Schedules adjusted for your family
- [ ] Notifications configured
- [ ] Guest mode tested
- [ ] Movie mode tested

---

## 🎉 You're Done When...

1. ✅ You can say "Alexa, good night" and the house shuts down
2. ✅ You can say "Alexa, good morning" and lights/blinds activate
3. ✅ You can say "Alexa, turn on Turkey Tom" and decorations turn on
4. ✅ Mode changes work from dashboard
5. ✅ Holiday decorations turn on/off automatically

---

## 📚 Next: Read Full Documentation

See `MODE_AUTOMATION_README.md` for:
- Detailed customization options
- Advanced scheduling
- Troubleshooting
- Adding more holidays
- Room-by-room customization

**Need Help?** Check the logs:
- Settings > System > Logs
- Filter by "script" or "automation"

**Happy Automating! 🏠✨**
