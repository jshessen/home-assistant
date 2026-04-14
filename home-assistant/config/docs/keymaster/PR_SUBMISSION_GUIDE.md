# How to Submit This Pull Request

## Context

**Previous PR**: #515 (merged Nov 7, 2025) - Fixed Schlage masked response bugs
**This PR**: Fixes issue #520 - Child locks stuck in "Deleting" when parent slot disabled
**Target Branch**: `beta` (for inclusion in next release)

## Prerequisites

1. ✅ Fork the keymaster repository: <https://github.com/FutureTense/keymaster>
2. ✅ Clone your fork locally
3. ✅ Create a new branch from `beta` (not `main`!)

**Important**: Since PR #515 is merged, make sure to pull the latest `beta` branch before creating your new branch.

## Steps

### 1. Update Your Fork with Latest Beta

```bash
cd /path/to/your/keymaster/fork
git checkout beta
git pull upstream beta  # Or: git pull origin beta
git push origin beta    # Update your fork
```

### 2. Create Feature Branch

```bash
git checkout -b fix/disabled-slot-sync-loop-520
```

### 3. Apply the Fix

Edit `custom_components/keymaster/coordinator.py` in the `_update_child_code_slots()` method.

**Find this code:**

```python
# Check if child PIN is masked (Schlage bug workaround)
child_pin = child_kmlock.code_slots[code_slot_num].pin
pin_mismatch = kmslot.pin != child_pin and not (
    child_pin and "*" in child_pin
)  # Ignore masked responses

_LOGGER.debug(
    "[_sync_child_locks] %s Slot %s: parent=%s child=%s mismatch=%s",
    child_kmlock.lock_name,
    code_slot_num,
    kmslot.pin,
    child_pin,
    pin_mismatch,
)
```

**Replace with:**

```python
# Check if child PIN is masked (Schlage bug workaround)
child_pin = child_kmlock.code_slots[code_slot_num].pin

# If parent slot is disabled or inactive, treat parent PIN as None for comparison
# to prevent endless clear loops when parent still has PIN in memory
parent_pin_for_comparison = (
    kmslot.pin if (kmslot.enabled and kmslot.active) else None
)

pin_mismatch = parent_pin_for_comparison != child_pin and not (
    child_pin and "*" in child_pin
)  # Ignore masked responses

_LOGGER.debug(
    "[_sync_child_locks] %s Slot %s: parent=%s (actual=%s, enabled=%s) child=%s mismatch=%s",
    child_kmlock.lock_name,
    code_slot_num,
    parent_pin_for_comparison,
    kmslot.pin,
    kmslot.enabled,
    child_pin,
    pin_mismatch,
)
```

### 4. Commit the Changes

```bash
git add custom_components/keymaster/coordinator.py
git commit -m "Fix: Child locks stuck in 'Deleting' when parent slot disabled

- Treat disabled/inactive parent slots as having no PIN for comparison
- Prevents infinite sync loop when parent slot disabled but retains PIN value
- Fixes issue #520

When a parent slot is disabled, the PIN text field may still contain
a value. The sync logic was comparing this stale PIN against cleared
child slots, causing false mismatch detection and endless clear loops.

Now uses parent_pin_for_comparison which is None when parent slot is
disabled or inactive, allowing proper sync status for child locks.

This is a follow-up to PR #515 which fixed Schlage masked response issues."
```

### 5. Push to Your Fork

```bash
git push origin fix/disabled-slot-sync-loop-520
```

### 6. Create Pull Request on GitHub

1. Go to <https://github.com/FutureTense/keymaster>
2. Click "Pull requests" → "New pull request"
3. Click "compare across forks"
4. Set:
   - **base repository**: `FutureTense/keymaster`
   - **base**: `beta` (NOT main or dev!)
   - **head repository**: `YOUR-USERNAME/keymaster`
   - **compare**: `fix/disabled-slot-sync-loop-520`
5. Click "Create pull request"
6. Use title: **Fix: Child locks stuck in "Deleting" status when parent slot is disabled (#520)**
7. Paste the description from `PR_DESCRIPTION.md`
8. Submit!

## Files Included for Reference

- `PR_DESCRIPTION.md` - Full PR description for GitHub
- `PR_FIX_SYNC_LOOP.md` - Detailed technical explanation
- `PR_FIX_SYNC_LOOP.patch` - Git patch file (alternative to manual editing)
- `PR_SUBMISSION_GUIDE.md` - This file (step-by-step instructions)

## Important Notes

- ✅ PR should target the `beta` branch (where PR #515 was merged)
- ✅ Reference issue #520 in the PR description
- ✅ Keep the commit message clear and descriptive
- ✅ The fix is minimal (8 lines changed) and backward compatible
- ✅ This is a follow-up to PR #515 (merged Nov 7, 2025)

## Testing Evidence to Include

If asked, you can provide:

- Tested with 4x Schlage BE469 locks (1 parent, 3 children)
- Z-Wave JS UI environment
- Verified no more infinite loops
- Child locks show "Disconnected" for disabled parent slots
- Z-Wave traffic normalized
- Active slots continue syncing correctly

## Relationship to PR #515

**PR #515** (merged Nov 7): Fixed Schlage masked response bugs

- Issue: Locks return masked PINs (`**********`) causing sync loops
- Fix: Handle masked responses and update child PIN in memory

**This PR** (new): Fixes disabled parent slot sync loop

- Issue: Disabled parent slots with stale PIN values cause infinite clears
- Fix: Treat disabled/inactive parent slots as having `pin=None`

Both PRs modify the same `_update_child_code_slots()` method but address different root causes.

- Active slots continue syncing correctly
