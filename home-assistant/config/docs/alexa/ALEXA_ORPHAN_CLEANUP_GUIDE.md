# Alexa Orphan Device Cleanup Guide

## Overview

The Alexa Orphan Device Cleanup Tool helps you identify and remove "orphaned" devices from your Alexa Smart Home skill. Orphaned devices are entities that Alexa still knows about, but your Home Assistant no longer exposes or should not expose.

This commonly happens when you:

- Rename devices in Home Assistant
- Remove integrations or devices
- Change your Alexa filter configuration (add exclude patterns)
- Reorganize your smart home setup
- Add new exclude patterns to filter out helper entities (like keymaster lock code slots)

## Quick Start

```bash
# Run the interactive tool
python3 /config/scripts/alexa_orphan_cleanup.py

# Or provide HAR file directly
python3 /config/scripts/alexa_orphan_cleanup.py --har ~/Downloads/developer.amazon.com.har

# Nuclear option - delete all and rediscover
python3 /config/scripts/alexa_orphan_cleanup.py --nuclear
```

## How It Works

### Step 1: Get Device List from Alexa

The tool needs to know what devices Alexa has stored. This information comes from the Amazon Developer Console.

**Instructions:**

1. Open your browser's Developer Tools (F12)
2. Go to the **Network** tab
3. Navigate to: <https://developer.amazon.com/alexa/console/ask/devices/>
4. Wait for the page to load completely (you should see your devices)
5. Right-click in the Network tab → **Save all as HAR with content** (or **Export HAR**)

**Security Note - Sanitized Export:**

Most browsers offer sanitized HAR export options that remove sensitive data:

- **Chrome/Edge**: Right-click → "Save all as HAR" (already sanitizes cookies by default)
- **Firefox**: Right-click → "Save All As HAR" → Check "Sanitize" option if available
- **Safari**: Export → HAR (cookies are typically excluded)

The HAR file will be 400KB+ in size. The script only needs the device data (JSON response from `/api/endpoints/ask`), not authentication cookies.

**After use, delete the HAR file** as it may still contain session information.

**Verify HAR File Sanitization (Optional but Recommended):**

You can verify your HAR file was properly sanitized before using it:

```bash
python3 << 'EOF'
import json

with open('/path/to/your/developer.amazon.com.har', 'r') as f:
    har_data = json.load(f)

# Check for cookies
total_cookies = 0
for entry in har_data['log']['entries']:
    total_cookies += len(entry['request'].get('cookies', []))
    total_cookies += len(entry['response'].get('cookies', []))

# Check for device data
devices_found = False
for entry in har_data['log']['entries']:
    if '/api/endpoints/ask' in entry['request']['url']:
        response_text = entry['response']['content'].get('text', '')
        if response_text:
            data = json.loads(response_text)
            devices_found = len(data.get('endpoints', [])) > 0
            break

print(f"✓ Total cookies in HAR: {total_cookies}")
print(f"✓ Device data present: {devices_found}")
print(f"\n{'✓ HAR file is SAFE to use' if total_cookies == 0 else '⚠ WARNING: HAR contains cookies'}")
EOF
```

Expected output for a properly sanitized file:

```text
✓ Total cookies in HAR: 0
✓ Device data present: True

✓ HAR file is SAFE to use
```

### Step 2: Get Device List from Home Assistant

The tool queries your Home Assistant configuration to determine what devices **should currently be exposed** to Alexa based on your configuration.

**How it works:**

1. Queries HA's REST API at `http://localhost:8123/api/states` for current entities
2. Falls back to reading `.storage/core.entity_registry` if API unavailable
3. Parses `alexa.yaml` to determine which domains are exposed (e.g., `light`, `switch`, `cover`)
4. **Loads and applies exclude patterns** from `alexa/exclude/*.yml` files
5. Filters entities based on your complete Alexa configuration

**Key Feature - Exclude Pattern Support:**

The tool now respects your `exclude_entity_globs` configuration! If you have exclude patterns like:

```yaml
# alexa/exclude/keymaster.yml
- switch.*_lock_code_slot_*
- binary_sensor.*_lock_code_slot_*
```

The tool will correctly identify these entities as "should not be exposed" and mark them as orphans if they're still in Alexa.

**No setup required** - the script handles this automatically when you run it.

### Step 3: Identify Orphans

The tool compares the two lists and applies your filter configuration:

- **Alexa devices** (from HAR file)
- **HA exposed devices** (from API/registry, filtered by include_domains AND exclude_entity_globs)

**Orphans** = Devices in Alexa but NOT currently exposed by HA (includes devices that match your exclude patterns)

**Example:**

If you have these keymaster entities in Alexa:

- `switch.front_door_lock_code_slot_1_enabled`
- `switch.front_door_lock_code_slot_2_enabled`

And you added exclude patterns:

```yaml
- switch.*_lock_code_slot_*
```

The tool will identify these as orphans because Home Assistant's Alexa integration now filters them out, even though they still exist in HA.

### Step 4: Cleanup

You have several options for removing orphans:

#### Option 1: Home Assistant Alexa Integration (Automated - Recommended)

The tool can automatically send DeleteReport events via Home Assistant's Alexa integration using stored OAuth tokens.

**Steps:**

1. Choose option `[1] Delete via Home Assistant (recommended)`
2. The script will:
   - Load cached OAuth tokens from `.storage/alexa_auth`
   - Refresh the token if needed (automatic)
   - Send DeleteReport events directly to Alexa Event Gateway
   - Process in batches of 50 devices
3. Confirm the deletion when prompted

**Advantages:**

- Uses Home Assistant's existing OAuth authentication
- No need to manually manage tokens
- Automatic token refresh
- Batched for reliability

The script will automatically submit all orphaned devices (including those that exist in HA but match exclude patterns) for deletion. No copy/pasting needed!

#### Option 2: Generate Service Call YAML (Copy/Paste)

For smaller lists or manual control:

1. Choose option `[2] Generate service call YAML`
2. Copy the generated YAML
3. Go to **Developer Tools → Services** in Home Assistant
4. Select `python_script.alexa_delete_devices`
5. Switch to **YAML mode**
6. Paste and execute

**Note:** For large orphan lists (100+ devices), this becomes unwieldy. Use Option 1 instead.

#### Option 3: Nuclear Option

Delete ALL Home Assistant devices from Alexa and rediscover from scratch.

**Pros:**

- Cleanest approach
- Removes ALL orphans (both deleted entities and pattern-matched entities)
- Fresh start
- Ensures Alexa exactly matches your current HA exposure configuration

**Cons:**

- Takes 10-15 minutes
- All Alexa routines need to be verified after

**To use:**

```bash
python3 /config/scripts/alexa_orphan_cleanup.py --nuclear
```

## Prerequisites

### Required

1. **Python 3.7+** (included with Home Assistant)

2. **python_script integration** in Home Assistant

   Add to `configuration.yaml`:

   ```yaml
   python_script:
   ```

3. **alexa_delete_devices.py** python script

   Already included at: `/config/python_scripts/alexa_delete_devices.py`

4. **Access to Home Assistant configuration directory**

   The script needs to read `/config/alexa.yaml` and query entity states

### Optional (for REST API automation)

- **requests** Python library (for automated API execution)

  Usually included with Home Assistant, or install with:

  ```bash
  pip3 install requests
  ```

- **Long-Lived Access Token** (for REST API calls)

  Create in your Home Assistant profile → Long-Lived Access Tokens

## File Locations

After running the tool, you'll find:

| File | Location | Purpose |
|------|----------|---------|
| Orphan list | `/config/scripts/alexa_orphans.txt` | Simple list of orphaned entity IDs |
| Detailed report | `/config/scripts/alexa_orphan_report_TIMESTAMP.txt` | Full analysis with stats |
| Tool script | `/config/scripts/alexa_orphan_cleanup.py` | The main Python script |
| Deletion script | `/config/python_scripts/alexa_delete_devices.py` | HA service for deletion |

## Examples

### Example 1: First Time Use

```bash
$ python3 /config/scripts/alexa_orphan_cleanup.py

╔══════════════════════════════════════════════════════════════════╗
║         🧹 Alexa Orphan Device Cleanup Tool 🧹                  ║
╚══════════════════════════════════════════════════════════════════╝

```

[INFO] Processing HAR file: /tmp/developer.amazon.com.har
[SUCCESS] Found 1200 devices in Alexa

[INFO] Extracting currently exposed devices from Home Assistant...
[INFO] Loaded 68 exclude patterns from alexa/exclude/
[SUCCESS] Found 324 devices currently exposed by Home Assistant (excluded 552)

[INFO] Identifying orphaned devices...
[WARNING] Found 876 orphaned devices (including 552 excluded by patterns)

╔══════════════════════════════════════════════════════════════════╗
║                     ORPHAN ANALYSIS RESULTS                      ║
╠══════════════════════════════════════════════════════════════════╣
║  Total devices in Alexa:            1200                        ║
║  Currently exposed by HA:            324                        ║
║  Orphaned devices:                   876                        ║
║    - Deleted/renamed in HA:          324                        ║
║    - Excluded by patterns:           552                        ║
╚══════════════════════════════════════════════════════════════════╝

[INFO] Sample orphaned devices (first 10):

- light.old_lamp_1                          (deleted)
- switch.removed_switch                     (deleted)
- switch.front_door_lock_code_slot_1_enabled (excluded)
- binary_sensor.back_door_lock_code_slot_2_active (excluded)
  ...

[SUCCESS] Report saved: /config/scripts/alexa_orphan_report_20251104_162245.txt
[INFO] Orphan list: /config/scripts/alexa_orphans.txt

╔══════════════════════════════════════════════════════════════════╗
║                       CLEANUP OPTIONS                            ║
╚══════════════════════════════════════════════════════════════════╝

  [1] Delete via Home Assistant (recommended)
  [2] Generate service call YAML
  [3] Nuclear option - delete ALL and rediscover
  [4] Cancel

Choose option (1-4): 1

[INFO] Loading OAuth tokens from Home Assistant storage...
[SUCCESS] Loaded access token (expires in 3245 seconds)
[INFO] Sending DeleteReport events in batches of 50...
[PROGRESS] Batch 1/18: 50 devices submitted
[PROGRESS] Batch 2/18: 50 devices submitted
...
[SUCCESS] All 876 devices submitted for deletion

### Example 2: Automated Workflow

```bash
# Provide HAR file upfront
python3 /config/scripts/alexa_orphan_cleanup.py --har /tmp/developer.amazon.com.har

# Or use auto-delete mode (skips confirmation)
python3 /config/scripts/alexa_orphan_cleanup.py --har /tmp/file.har --auto-delete
```

## Troubleshooting

### "Could not extract devices from HAR file"

**Cause:** The HAR file doesn't contain the devices API response.

**Solution:**

1. Make sure the devices page fully loaded before saving HAR
2. Look for 1200+ devices displayed in the UI
3. Save the HAR file AFTER the page loads
4. Run the HAR validation script (see Step 1) to verify device data is present

### "HAR file contains cookies - is this safe?"

**Cause:** Your browser didn't sanitize the HAR export, or you're unsure about security.

**Solution:**

1. Run the HAR validation script from Step 1 to check cookie count
2. If cookies are present (count > 0):
   - Re-export using "Save all as HAR" (Chrome/Edge auto-sanitizes)
   - In Firefox, ensure "Sanitize" option is checked
   - Or continue with caution and **delete HAR immediately after use**
3. The script only reads device data from `/api/endpoints/ask` response, not cookies
4. Always delete HAR files after use regardless of sanitization

### "Cannot access /config directory" or "alexa.yaml not found"

**Cause:** Script cannot find Home Assistant configuration.

**Solution:**

1. Run the script from within your Home Assistant system (not remotely)
2. Ensure you're in the `/config` directory or a subdirectory
3. Verify `alexa.yaml` exists in `/config/`

### "Could not determine exposed devices"

**Cause:** Unable to query Home Assistant API or read entity registry.

**Solution:**

1. Check if Home Assistant is running: `docker ps | grep homeassistant`
2. Verify API is accessible: `curl http://localhost:8123/api/`
3. Check file permissions on `/config/.storage/core.entity_registry`

### "API request failed" when using REST API option

**Cause:** Invalid access token or API unavailable.

**Solution:**

1. Verify your Long-Lived Access Token is valid
2. Check token hasn't expired (recreate if needed)
3. Ensure Home Assistant API is accessible
4. Use the curl command option instead (reads from saved file)

### "requests library not available"

**Cause:** Python requests library not installed (rare).

**Solution:**

```bash
# System-wide (if needed)
pip3 install requests

# Or in Home Assistant container
docker exec -it home-assistant pip3 install requests
```

## Advanced Usage

### Automated Execution with Access Token

Store your token securely and automate cleanup:

```bash
#!/bin/bash
# Weekly cleanup script

# Store token in environment or secrets manager
export HA_TOKEN="your_long_lived_token"

# Run cleanup with auto-execution
python3 /config/scripts/alexa_orphan_cleanup.py \
  --har /tmp/latest.har \
  --auto-delete
```

### Batch Processing with Curl

For extremely large orphan lists, process in batches:

```bash
# Split orphan list into batches of 100
split -l 100 /config/scripts/alexa_orphans.txt /tmp/batch_

# Delete each batch
for batch in /tmp/batch_*; do
  echo "Processing $batch..."

  python3 -c "
import json
with open('$batch', 'r') as f:
    entities = [line.strip() for line in f if line.strip()]
print(json.dumps({'entity_ids': entities}))
" | curl -X POST http://localhost:8123/api/services/python_script/alexa_delete_devices \
    -H 'Authorization: Bearer $HA_TOKEN' \
    -H 'Content-Type: application/json' \
    -d @-

  # Wait between batches
  sleep 5
done
```

### Integration with CI/CD

```bash
#!/bin/bash
# Weekly cleanup script

# Download latest HAR (requires automation)
./download_har.sh

# Run cleanup
python3 /config/scripts/alexa_orphan_cleanup.py \
  --har /tmp/latest.har \
  --auto-delete

# Send notification
curl -X POST http://ha:8123/api/services/notify/mobile_app \
  -d '{"message": "Alexa cleanup complete"}'
```

## FAQ

**Q: Will this affect other Alexa skills?**
A: No. This only affects devices from your Home Assistant skill.

**Q: Can I undo the deletion?**
A: Yes. Just trigger Alexa discovery and HA will re-expose the devices (except those matching exclude patterns).

**Q: Why are devices showing as orphans even though they exist in HA?**
A: The script now respects your `exclude_entity_globs` configuration. If an entity matches an exclude pattern (like `switch.*_lock_code_slot_*` for keymaster entities), it's marked as an orphan because it shouldn't be exposed to Alexa. This is intentional cleanup.

**Q: How do I know which entities are excluded?**
A: The script loads patterns from `alexa/exclude/*.yml` files and logs how many patterns were loaded. Check your `alexa.yaml` configuration for the `exclude_entity_globs` directive.

**Q: How often should I run this?**
A: Run it whenever you make significant changes to your HA setup (new integrations, renaming devices, updating exclude patterns), or quarterly as maintenance.

**Q: What's the "nuclear option"?**
A: It deletes ALL HA devices from Alexa and rediscovers from scratch. Use this for a clean slate when you've made extensive configuration changes.

**Q: Is the HAR file secure?**
A: Modern browsers can export sanitized HAR files that exclude sensitive cookies. Chrome/Edge sanitize by default, Firefox has a "Sanitize" option. The script only needs the API response data, not authentication cookies. Always delete HAR files after use and never share them publicly.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review Home Assistant logs: `tail -f /config/home-assistant.log`
3. Check CloudWatch logs: `aws logs tail /aws/lambda/HomeAssistant`
4. File an issue in the repository

## See Also

- [alexa_delete_devices.py](/config/python_scripts/alexa_delete_devices.py) - The deletion script
- [Amazon Alexa Smart Home Documentation](https://developer.amazon.com/docs/device-apis/alexa-discovery.html)
- [Home Assistant Alexa Integration](https://www.home-assistant.io/integrations/alexa/)
