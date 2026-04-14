# Alexa OAuth Bug Fix

## Problem

Home Assistant 2025.11.0 introduced a bug in the Alexa integration that prevents OAuth authentication from working. When attempting to link the Alexa Smart Home skill, users receive:

- **Error in Alexa app**: "unable to link the skill at this time"
- **Error in HA logs**: `TypeError: can't compare offset-naive and offset-aware datetimes`

**GitHub Issue**: <https://github.com/home-assistant/core/issues/155886>

## Quick Fix

Run the automated fix script:

```bash
cd /opt/docker/home-assistant
./scripts/fix-alexa-oauth-bug.sh
```

Then restart Home Assistant:

```bash
docker restart home-assistant
# or
make restart
```

## When to Reapply This Fix

You'll need to reapply this fix after:

1. **Upgrading Home Assistant container** - Any time you pull a new HA image
2. **Rebuilding containers** - If you run `docker-compose up --build`
3. **Clearing container data** - If you recreate the container from scratch

**Signs you need to reapply:**

- Alexa skill linking fails with "unable to link the skill at this time"
- Logs show `TypeError: can't compare offset-naive and offset-aware datetimes` in alexa/auth.py

## What the Fix Does

The script:

1. ✓ Checks if Home Assistant container is running
2. ✓ Creates a backup of the original file (if not already backed up)
3. ✓ Detects if the fix is already applied (safe to run multiple times)
4. ✓ Patches line 113 in `/usr/src/homeassistant/homeassistant/components/alexa/auth.py`
5. ✓ Verifies the patch was applied correctly

**The actual code change:**

```python
# BEFORE (buggy):
return dt_util.utcnow() < preemptive_expire_time

# AFTER (fixed):
return dt_util.utcnow() < dt_util.as_utc(preemptive_expire_time)
```

## Manual Fix (if script doesn't work)

```bash
# Create backup
docker exec home-assistant cp \
  /usr/src/homeassistant/homeassistant/components/alexa/auth.py \
  /usr/src/homeassistant/homeassistant/components/alexa/auth.py.backup

# Apply fix
docker exec home-assistant sed -i \
  's/return dt_util\.utcnow() < preemptive_expire_time/return dt_util.utcnow() < dt_util.as_utc(preemptive_expire_time)/' \
  /usr/src/homeassistant/homeassistant/components/alexa/auth.py

# Restart
docker restart home-assistant
```

## Restore Original (Rollback)

If you need to undo the fix:

```bash
docker exec home-assistant cp \
  /usr/src/homeassistant/homeassistant/components/alexa/auth.py.backup \
  /usr/src/homeassistant/homeassistant/components/alexa/auth.py

docker restart home-assistant
```

## When You Can Stop Using This Fix

Monitor the GitHub issue: <https://github.com/home-assistant/core/issues/155886>

Once the issue is marked as **Closed** or **Fixed**:

1. Check the release notes for the version mentioned in the issue
2. Update Home Assistant to that version or later
3. The fix will be included in the official release
4. You no longer need to apply this patch

**To check your current HA version:**

```bash
docker exec home-assistant python -m homeassistant --version
```

## Troubleshooting

**Script says "already applied" but Alexa still doesn't work:**

- Check if there are other errors in the logs: `tail -f home-assistant/config/home-assistant.log`
- Verify Alexa configuration is correct
- Check AWS Lambda logs if using external authentication

**Script fails with "container not running":**

- Start Home Assistant first: `cd /opt/docker/home-assistant && make hacs`
- Or check container status: `docker ps | grep home-assistant`

**Want to verify the fix is applied:**

```bash
docker exec home-assistant grep -n "dt_util.as_utc(preemptive_expire_time)" \
  /usr/src/homeassistant/homeassistant/components/alexa/auth.py
```

Should show line 113 with the fixed code.

## Technical Details

**Root Cause:**

- `dt_util.utcnow()` returns timezone-aware datetime
- `dt_util.parse_datetime()` returns timezone-naive datetime
- Python 3.12+ strictly prohibits comparing these two types

**Why This Happened:**

- Regression introduced in Home Assistant 2025.11.0
- Likely related to Python 3.13 upgrade or datetime utility changes

**Official Fix Status:**

- Reported: November 5, 2025
- Assigned to: @ochlocracy and @jbouwh (Alexa code owners)
- Expected fix: Likely in next patch release (2025.11.1 or 2025.12.0)
