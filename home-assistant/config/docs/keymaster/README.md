# Keymaster Lock Code Management

This directory contains documentation related to the Keymaster custom integration for managing Z-Wave lock codes.

## Integration Details

- **Version**: v0.1.1-b1 (custom build with Schlage BE469 fixes)
- **Repository**: <https://github.com/FutureTense/keymaster>
- **Location**: `/config/custom_components/keymaster/`

## Locks Managed

This configuration manages 4 Schlage locks in a parent-child relationship:

- **Parent**: Front Door Lock (BE469)
- **Children**:
  - Back Door Lock (BE469)
  - Kitchen Entry Lock (BE469)
  - Garage Entry Lock (FE599)

## Upstream Contributions

This directory contains documentation for bug fixes contributed back to the keymaster project.

### Parent-Child Sync Loop Fix (Issue #520)

**Problem**: Child locks stuck in "Deleting" status when parent slot disabled, causing infinite Z-Wave traffic.

**Documentation**:

- **PR_SUBMISSION_GUIDE.md** - Step-by-step instructions for submitting the PR
- **PR_DESCRIPTION.md** - GitHub PR description ready to paste
- **PR_FIX_SYNC_LOOP.md** - Technical deep-dive explanation of the fix
- **PR_FIX_SYNC_LOOP.patch** - Git patch file (alternative to manual editing)

**Issue Reference**: <https://github.com/FutureTense/keymaster/issues/520>

**Status**: Ready for submission to upstream `dev` branch

## Configuration Files

Keymaster configuration is spread across several locations:

### Scripts

- `scripts/keymaster_front_door_lock_manual_notify.yaml`
- `scripts/keymaster_back_door_lock_manual_notify.yaml`
- `scripts/keymaster_kitchen_door_lock_manual_notify.yaml`
- `scripts/keymaster_garage_entry_lock_manual_notify.yaml`
- `scripts/keymaster_manual_notify_master.yaml`

### Lovelace Dashboards

- `lovelace/keymaster.yaml` - Main dashboard include
- `custom_components/keymaster/lovelace/*.yaml` - Auto-generated per-lock dashboards

### Entity Patterns

- Locks: `lock.touchscreen_deadbolt_<location>`
- Code slots: `sensor.*_code_slot_*`
- Enabled switches: `switch.*_lock_code_slot_*_enabled`

## Known Issues & Fixes

### Schlage BE469 Masked PIN Responses

**Issue**: Schlage BE469 locks sometimes return masked PINs (with `*` characters) instead of clearing them.

**Workaround**: Keymaster includes logic to ignore masked responses during PIN comparison.

**Code Location**: `custom_components/keymaster/coordinator.py` - `_update_child_code_slots()` method

### Parent-Child Sync Loop (Fixed)

**Issue**: When a parent slot is disabled but retains a PIN value in memory, child locks get stuck in endless clear loops.

**Fix**: Treat disabled/inactive parent slots as having no PIN for comparison purposes.

**Status**: Fix developed and tested, ready for upstream submission (see PR documentation).

## Testing Environment

- **Home Assistant**: Docker container (host network mode)
- **Z-Wave**: Z-Wave JS UI on port 8091
- **Locks**: 4x Schlage (3x BE469, 1x FE599)
- **Network**: Z-Wave mesh with 80+ devices, including multiple repeaters

## Resources

- **Official Docs**: <https://github.com/FutureTense/keymaster/wiki>
- **Issue Tracker**: <https://github.com/FutureTense/keymaster/issues>
- **Community**: Home Assistant Community Forum
