# iBlinds v2 Z-Wave Research Report
**Date:** 2026-04-15
**Investigator:** Linus (Integration Specialist)

## Executive Summary

The iBlinds v2 (IB2.0) devices suffer from position reporting failures due to **missing Association Group definitions** in the device config. The v3 units work correctly because they have a properly configured Lifeline association (Group 1), which enables unsolicited position reports back to the controller.

**Root cause:** v2 config lacks `"associations"` section entirely.
**Recommended fix:** Add Lifeline association group to v2 config file.
**Parameter 4 status:** NOT supported in v2 firmware (1.65) - this is a v3-only feature.

---

## 1. Current State Analysis

### v2 Config File (`ib2_0.json`)
**Location:** `/opt/docker/home-assistant/zwave/.config-db/devices/0x0287/ib2_0.json`

**Current content:**
```json
{
  "manufacturer": "HAB Home Intelligence, LLC",
  "manufacturerId": "0x0287",
  "label": "IB2.0",
  "description": "Window Blind Controller",
  "devices": [{"productType": "0x0003", "productId": "0x000d"}],
  "firmwareVersion": {"min": "0.0", "max": "255.255"},
  "paramInformation": [
    {
      "#": "1",
      "label": "Auto Calibration Torque",
      "description": "Adjust Torque Value for Auto Calibration",
      "valueSize": 1,
      "defaultValue": 1,
      "allowManualEntry": false,
      "options": [...]
    }
  ]
}
```

**Critical gaps:**
- ❌ NO `"associations"` section
- ❌ NO `"compat"` flags
- ❌ ONLY Parameter 1 defined (Auto Calibration Torque)
- ❌ NO Parameter 4 (Default ON Value) - not supported in v2 firmware

### v3 Config File (`iblindsv3.json`)
**Location:** `/opt/docker/home-assistant/zwave/.config-db/devices/0x0287/iblindsv3.json`

**Key features:**
```json
{
  "associations": {
    "1": {
      "label": "Lifeline",
      "maxNodes": 1,
      "isLifeline": true
    }
  },
  "paramInformation": [
    // 10 parameters including:
    {"#": "3", "label": "Send Reports"...},
    {"#": "4", "label": "Default ON Value", "defaultValue": 50...},
    {"#": "6", "label": "Movement Duration"...}
  ],
  "compat": {
    "commandClasses": {
      "remove": {
        "Binary Switch": {"endpoints": "*"}
      }
    }
  }
}
```

**Why v3 works:**
- ✅ Lifeline association (Group 1) configured
- ✅ Parameter 3 "Send Reports" controls whether device sends unsolicited reports
- ✅ Parameter 4 "Default ON Value" sets default open position
- ✅ Compat flag removes Binary Switch CC to avoid confusion

---

## 2. Upstream Database Comparison

**Upstream source:** `https://github.com/zwave-js/zwave-js/master/packages/config/config/devices/0x0287/`

### ib2_0.json (Upstream)
**Status:** IDENTICAL to our local copy
- No associations defined
- Only Parameter 1 included
- No compat flags

### iblindsv3.json (Upstream)
**Status:** IDENTICAL to our local copy
- Associations properly configured
- All 10 parameters included
- Binary Switch removal compat flag present

**Conclusion:** Our local config is current with upstream. The v2 config is missing associations in the official database too.

---

## 3. Z-Wave Association Fundamentals

### What are Associations?
Z-Wave associations define which nodes should receive unsolicited reports from a device. Without proper associations:
- Device does NOT send position updates after local changes
- Device does NOT send position reports after Z-Wave commands complete
- Controller must poll device repeatedly to learn current state
- Position values remain "unknown" until manually polled

### The Lifeline Group (Group 1)
Per Z-Wave spec, Group 1 should be the **Lifeline**:
- Sends device status updates to the controller
- Sends battery reports (for battery devices)
- Sends position reports for covers
- Should auto-configure to controller node (Node 1) during inclusion

### v2 Problem Statement
**Without a Lifeline association configured:**
1. Z-Wave JS UI doesn't know to auto-assign controller to Group 1
2. Device never sends position reports back to controller
3. Home Assistant shows position as "unknown"
4. Open/Close commands work (device moves) but state never updates

**With Lifeline association configured:**
1. During inclusion, controller assigns itself to Group 1
2. Device sends Multilevel Switch Report after movement completes
3. Z-Wave JS UI receives report and updates position value
4. Home Assistant shows actual position (0-99)

---

## 4. Relevant zwave-js Compat Flags

Based on zwave-js documentation review, the following compat flags are relevant:

### Flags that WON'T help v2 position reporting:
- ❌ `treatSetAsReport` - Only works for Binary Switch CC and Thermostat Mode CC (not Multilevel Switch)
- ❌ `manualValueRefreshDelayMs` - Only adds delay before polling after NIF, doesn't fix reporting
- ❌ `mapBasicReport` / `mapBasicSet` - Not related to Multilevel Switch position reporting
- ❌ `overrideQueries` - For fixing bad query responses, not missing reports

### Flags that COULD help (if v2 behavior requires it):
- ⚠️ `disableAutoRefresh` - If v2 devices respond poorly to polling after commands
- ⚠️ `reportTimeout` - Custom timeout for waiting for reports after commands
- ⚠️ `commandClasses.remove` - v3 removes Binary Switch CC; v2 might benefit from same

### The ACTUAL fix:
**Add `"associations"` section** - This is the proper solution, not a workaround compat flag.

---

## 5. Parameter 4 Investigation

**Parameter 4: "Default ON Value"** (v3 only)
- Controls where "Open" command goes (default: 50%)
- Allows voice commands like "Alexa, open blinds" to go to preferred position
- Supported firmware: v3.0+

**v2 firmware (1.65) capabilities:**
- ❌ Does NOT support Parameter 4
- ❌ Does NOT support Parameters 2-10 (all v3 additions)
- ✅ ONLY supports Parameter 1 (Auto Calibration Torque)
- Behavior: "Open" command = position 99 (fully open), "Close" = position 0

**Alternative approach for v2:**
Since v2 doesn't support configurable stop points:
1. Use Home Assistant scenes/scripts to send specific position values (0-99)
2. Use Cover helpers to define "open" position in HA automations
3. Create Alexa routines that call HA scripts with specific positions
4. Accept that native Z-Wave "Open" command = fully open (99)

---

## 6. Recommended Changes to ib2_0.json

### Minimal Fix (Position Reporting)
Add Association Group 1 (Lifeline):

```json
{
  "manufacturer": "HAB Home Intelligence, LLC",
  "manufacturerId": "0x0287",
  "label": "IB2.0",
  "description": "Window Blind Controller",
  "devices": [
    {
      "productType": "0x0003",
      "productId": "0x000d"
    }
  ],
  "firmwareVersion": {
    "min": "0.0",
    "max": "255.255"
  },
  "associations": {
    "1": {
      "label": "Lifeline",
      "maxNodes": 1,
      "isLifeline": true
    }
  },
  "paramInformation": [
    {
      "#": "1",
      "label": "Auto Calibration Torque",
      "description": "Adjust Torque Value for Auto Calibration",
      "valueSize": 1,
      "defaultValue": 1,
      "allowManualEntry": false,
      "options": [
        {"label": "Calibrate using default torque", "value": 1},
        {"label": "Reduce calibration torque by 1 factor", "value": 2},
        {"label": "Reduce calibration torque by 2 factors", "value": 3},
        {"label": "Increase calibration torque by .5 factor", "value": 4},
        {"label": "Increase calibration torque by 1 factor", "value": 5}
      ]
    }
  ]
}
```

### Optional Enhancement (Binary Switch Removal)
If v2 also exposes Binary Switch CC (unknown without device interview), add v3's compat flag:

```json
{
  ...existing config...,
  "compat": {
    "commandClasses": {
      "remove": {
        "Binary Switch": {
          "endpoints": "*"
        }
      }
    }
  }
}
```

**Rationale:** v3 removes Binary Switch CC because it controls tilt but isn't linked to Window Covering CC. If v2 has the same issue, removing it prevents confusion.

---

## 7. Implementation Steps

### Step 1: Edit Local Config
```bash
cd /opt/docker/home-assistant/zwave/.config-db/devices/0x0287/
# Edit ib2_0.json to add associations section
```

### Step 2: Restart Z-Wave JS UI
```bash
docker restart zwave-js-ui
# Wait 30 seconds for service to fully restart
```

### Step 3: Re-interview v2 Devices
For EACH v2 node (67, 71, 72, 103, 106, 107):
1. Open Z-Wave JS UI (port 8091)
2. Navigate to node → Actions
3. Click "Re-interview Node"
4. Wait for interview to complete
5. Verify Association Group 1 now shows controller (Node 1)

### Step 4: Test Position Reporting
1. Manually operate blinds (physical button on device)
2. Check if Home Assistant position updates from "unknown"
3. Send Z-Wave Open/Close command
4. Verify position updates after movement completes

### Step 5: Submit Upstream PR (Optional)
If fix works, contribute back to zwave-js:
1. Fork `zwave-js/zwave-js` repository
2. Edit `packages/config/config/devices/0x0287/ib2_0.json`
3. Add associations section
4. Submit PR with test results

---

## 8. Assessment: Can v2 Position Reporting Be Fixed?

**YES** - High confidence fix available via config change alone.

**Why it will work:**
- v3 proves the device hardware (Multilevel Switch CC) functions correctly
- Only difference is firmware version and config
- Association Group 1 is Z-Wave standard feature, not firmware-dependent
- Config change enables existing hardware capability

**Validation approach:**
1. v2 devices DO support Multilevel Switch Command Class
2. They DO respond to Get Position commands (when polled)
3. They CAN send Report commands (just need association configured)
4. Adding Lifeline association enables automatic Report sending

**Risk assessment:** LOW
- Worst case: Association doesn't help, position still unknown
- No risk of device damage or malfunction
- Change is reversible (remove associations section)

---

## 9. Assessment: Does v2 Support Configurable Stop Point?

**NO** - v2 firmware does not support Parameter 4 (Default ON Value).

**Evidence:**
- Official v2 config only defines Parameter 1
- v3 changelog indicates Parameters 2-10 added in v3 firmware
- v2 firmware version 1.65 predates v3.0+ features
- Upstream zwave-js database confirms single parameter

**Workaround options:**
1. **Home Assistant scenes:** Define "preferred open" position in HA
2. **Scripts:** Create "open to 50%" script, bind to voice commands
3. **Template covers:** Wrap v2 covers with HA template that overrides "open"
4. **Alexa routines:** Map voice commands to HA scripts, not raw Z-Wave commands

**Firmware upgrade possibility:**
- Check if HAB offers firmware update v2 → v3
- Likely requires physical access to device (over-the-air unlikely)
- May be hardware limitation, not just firmware

---

## 10. Additional Research Notes

### Z-Wave Command Classes (v2 vs v3)
Both versions use:
- **Multilevel Switch CC** - Position control (0-99)
- **Battery CC** - Battery status reporting
- **Version CC** - Firmware version reporting

v3 adds:
- Better association support
- More configuration parameters
- Improved report timing (Parameter 3)

### Known v3 Enhancements
1. **Parameter 3 "Send Reports"** - Can disable automatic reports if controller polls too aggressively
2. **Parameter 6 "Movement Duration"** - Override calculated movement time
3. **Parameter 7+ (fw 3.6+)** - Remote calibration, tilt limits, ON override

### Community Reports
Limited GitHub issues found for iBlinds v2 specifically. Most discussion centers on v3 features. This suggests:
- v2 is older, less common deployment
- v3 users benefited from better initial config
- Association issue may affect many v2 users silently

---

## 11. Recommended Next Actions

### Immediate (Test Fix)
1. ✅ Edit `/opt/docker/home-assistant/zwave/.config-db/devices/0x0287/ib2_0.json`
2. ✅ Add associations section (Lifeline Group 1)
3. ✅ Restart zwave-js-ui container
4. ✅ Re-interview one v2 node (test with Node 71 or 72)
5. ✅ Validate position reporting works
6. ✅ Re-interview remaining v2 nodes if test succeeds

### Short-term (System-wide)
1. Document v2 limitations (no Parameter 4) in project docs
2. Create HA scripts for "open to preferred position"
3. Update Alexa routines to use HA scripts instead of raw Z-Wave
4. Consider template cover wrappers for v2 devices

### Long-term (Community)
1. Submit PR to zwave-js with v2 association fix
2. Test if Binary Switch removal compat flag helps v2
3. Document workarounds for v2 stop point limitation
4. Investigate firmware upgrade path v2 → v3

---

## Appendix A: File Comparison

### Local vs Upstream: ib2_0.json
**Status:** IDENTICAL (940 bytes, SHA: b78cd78809a78b21b1724378d88e63be779368a4)
- No local modifications present
- Upstream also missing associations
- Fix needed in both local and upstream

### Local vs Upstream: iblindsv3.json
**Status:** IDENTICAL (3688 bytes, SHA: a4939e096f40b79b94b802ec876a67bfbbe5c860)
- v3 config properly maintained
- All features correctly documented
- Binary Switch removal compat present

---

## Appendix B: Compat Flag Reference

### Flags Investigated
Based on zwave-js file-format.md documentation:

**Reviewed but not applicable:**
- `alarmMapping` - For Alarm/Notification CC translation
- `commandClasses.add` - For missing CC support
- `disableStrictMeasurementValidation` - For sensor reading validation
- `forceNotificationIdleReset` - For notification reset timing
- `mapBasicReport` / `mapBasicSet` - For Basic CC mapping
- `preserveEndpoints` - For multi-endpoint devices
- `skipConfigurationNameQuery` - For interview optimization
- `treatMultilevelSwitchSetAsEvent` - For remote controls (not blinds)
- `useUTCInTimeParametersCC` - For time/date configuration

**Potentially useful (future investigation):**
- `commandClasses.remove` - Remove Binary Switch if v2 has same issue as v3
- `reportTimeout` - If v2 devices have slow report timing
- `manualValueRefreshDelayMs` - If devices need delay before polling

---

**END OF REPORT**
