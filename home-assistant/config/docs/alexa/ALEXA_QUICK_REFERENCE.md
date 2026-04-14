# Alexa Device Deletion - Quick Reference

## 🎯 The Solution: Use Home Assistant's Built-in DeleteReport API

**No cookie sniffing needed!** Home Assistant already supports the official Alexa Smart Home API for device deletion.

---

## ⚡ Quick Start (3 Methods)

### Method 1: Bash Script (Easiest)

```bash
# Interactive menu
./alexa_cleanup.sh

# Remove specific device
./alexa_cleanup.sh light.old_lamp

# Remove pattern
./alexa_cleanup.sh "sensor.old_*"
```

### Method 2: Developer Tools → Services

```yaml
service: python_script.alexa_delete_devices
data:
  entity_ids:
    - light.unwanted_device
    - sensor.duplicate_sensor
```

### Method 3: REST API

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_ids": ["light.old_lamp"]}' \
  http://localhost:8123/api/services/python_script/alexa_delete_devices
```

---

## 📋 Setup (One-time, already done!)

1. ✅ `python_script:` added to `configuration.yaml`
2. ✅ Python script created: `python_scripts/alexa_delete_devices.py`
3. ✅ Helper script created: `scripts/alexa_device_cleanup.yaml`
4. ✅ Bash helper: `alexa_cleanup.sh`

**All you need to do:** Restart Home Assistant!

```bash
docker restart homeassistant
# or
make restart
```

---

## 🔍 How to Find Entity IDs to Remove

### Option 1: Developer Tools → States

Search for entities you want removed

### Option 2: Template in Developer Tools → Template

```yaml
{{ states
   | selectattr('domain', 'in', ['light', 'switch', 'cover', 'lock'])
   | map(attribute='entity_id')
   | list }}
```

### Option 3: Check Alexa App

Device names usually match HA friendly names

---

## ✅ Verification

1. **Home Assistant logs:**

   ```bash
   tail -f home-assistant/config/home-assistant.log | grep -i deletereport
   ```

2. **Alexa App:**
   - Devices should disappear in 1-2 minutes
   - Force close/reopen if needed

3. **Prevent re-discovery:**
   Add exclusions to `alexa/exclude/` directory

---

## 🆚 Why This Beats Cookie Sniffing

| Feature | Cookie Script | This Solution |
|---------|--------------|---------------|
| **Ease of Use** | ❌ HTTP sniffers, mobile setup | ✅ One command |
| **Security** | ❌ Extract auth tokens | ✅ Uses HA's OAuth |
| **Reliability** | ❌ Breaks with app updates | ✅ Official API |
| **Automation** | ❌ Manual cookie refresh | ✅ Fully automated |
| **Integration** | ❌ External Python script | ✅ Native HA |

---

## 📚 Full Documentation

See: `ALEXA_DEVICE_DELETION_GUIDE.md`

---

## 🔗 References

- **Amazon API Docs:** <https://developer.amazon.com/docs/device-apis/alexa-discovery.html#deletereport-event>
- **HA Source:** `homeassistant/components/alexa/state_report.py::async_send_delete_message()`

---

## 💡 Pro Tips

**Bulk delete by pattern:**

```bash
# Remove all old Z-Wave entities
./alexa_cleanup.sh "zwave.*"

# Remove all HACS-installed sensors
./alexa_cleanup.sh "sensor.hacs_*"
```

**Auto-cleanup on entity removal:**

```yaml
# Add to automations/
- alias: "Alexa: Auto-remove deleted entities"
  trigger:
    - platform: event
      event_type: entity_registry_updated
      event_data:
        action: remove
  action:
    - service: python_script.alexa_delete_devices
      data:
        entity_ids: "{{ [trigger.event.data.entity_id] }}"
```

**Prevent future issues:**
Add exclusions to `alexa/exclude/unwanted.yaml`:

```yaml
# Exclude all battery sensors
- sensor.*_battery
- sensor.*_battery_level

# Exclude diagnostic entities
- sensor.*_rssi
- sensor.*_last_seen
```

---

## ❓ Troubleshooting

### "Alexa integration not configured"

- Your `alexa.yaml` is fine, just restart HA

### "Invalid token"

- Relink HA skill in Alexa app

### Devices reappear

- They're still in HA and being re-exposed
- Add to `alexa/exclude/` or delete from HA

---

**Bottom line:** You already have everything you need. No cookie sniffing required! 🎉
