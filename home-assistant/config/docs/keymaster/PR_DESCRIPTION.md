# Pull Request for keymaster

## PR Title

Fix: Child locks stuck in "Deleting" status when parent slot is disabled (#520)

## Breaking change

None - This PR does not introduce breaking changes. The fix only modifies the comparison logic in `_update_child_code_slots()` to account for disabled/inactive parent slots, which is a defensive fix that prevents false mismatch detection.

## Proposed change

Fixes issue #520 where child locks get stuck in an infinite "Deleting" sync loop when a parent lock has a code slot disabled but the PIN text field still contains a value.

### Issue #520 - Child Locks Stuck in "Deleting" Status

When a parent lock has a code slot **disabled** (enabled=False) but the PIN text field still retains a value in memory, child locks get stuck in an infinite sync loop with "Deleting" status. This occurs because:

1. User disables a code slot on the parent lock
2. Child locks successfully clear the PIN (confirmed at Z-Wave level)
3. Sync logic compares:
   - Parent PIN: `"5979"` (still in memory from text field, even though disabled)
   - Child PIN: `None` (successfully cleared)
   - Result: **Mismatch detected** → Try to clear child again
4. Loop repeats every 15 seconds

This causes:

- Z-Wave controller saturation with repeated clear commands
- Child locks stuck showing "Deleting" status indefinitely
- Excessive Z-Wave traffic every 15 seconds
- User confusion about slot status

### Solution

Treat disabled or inactive parent slots as having `pin=None` for comparison purposes:

```python
# If parent slot is disabled or inactive, treat parent PIN as None for comparison
# to prevent endless clear loops when parent still has PIN in memory
parent_pin_for_comparison = (
    kmslot.pin if (kmslot.enabled and kmslot.active) else None
)

pin_mismatch = parent_pin_for_comparison != child_pin and not (
    child_pin and "*" in child_pin
)
```

This prevents false mismatch detection when parent slots are disabled but retain PIN values in memory.

## Changes Made

### Fix `_update_child_code_slots` PIN Comparison Logic (line ~2142)

**Before:**

```python
child_pin = child_kmlock.code_slots[code_slot_num].pin
pin_mismatch = kmslot.pin != child_pin and not (
    child_pin and "*" in child_pin
)
```

**After:**

```python
child_pin = child_kmlock.code_slots[code_slot_num].pin

# If parent slot is disabled or inactive, treat parent PIN as None for comparison
# to prevent endless clear loops when parent still has PIN in memory
parent_pin_for_comparison = (
    kmslot.pin if (kmslot.enabled and kmslot.active) else None
)

pin_mismatch = parent_pin_for_comparison != child_pin and not (
    child_pin and "*" in child_pin
)
```

This ensures parent slots that are disabled or inactive are treated as having no PIN for comparison purposes, preventing false mismatch detection.

## Diagnostic Process - How Issue Was Identified

### Home Assistant Keymaster Logs

Child lock sync showing infinite loop:

```log
[_sync_child_locks] Back Door Lock Slot 1: parent=5979 child=None mismatch=True
[_sync_child_locks] Back Door Lock Slot 1: parent=5979 child=None mismatch=True
[_sync_child_locks] Back Door Lock Slot 1: parent=5979 child=None mismatch=True
[Loop repeats every 15 seconds...]
```

Root cause: Parent slot disabled (`enabled=False`) but PIN still in memory, causing continuous mismatch detection against successfully cleared child slots.

### Z-Wave JS UI Log Analysis

Repeated clear commands to child locks:

```log
16:39:46 - userCode-1: ********** =>  (clearing)
16:39:56 - userCode-1:  =>  (still empty)
16:40:11 - userCode-1:  =>  (clearing AGAIN)
16:40:26 - userCode-1:  =>  (clearing AGAIN)
[Cycle repeats indefinitely...]
```

Child locks repeatedly receiving clear commands even though slots already empty at Z-Wave level.

## Testing Results

### Hardware Tested

- **Locks**: 4x Schlage BE469 Touchscreen Deadbolt (1 parent, 3 children)
- **Z-Wave**: Z-Wave JS UI
- **Scenario**: Disabled code slot on parent lock while PIN text field retained value

### Before Fix

- ✗ Infinite "Deleting" status on child locks
- ✗ Sync loop repeating every 15 seconds
- ✗ 50+ unnecessary Z-Wave clear commands over 10 minutes
- ✗ Excessive Z-Wave traffic
- ✗ Child lock status never resolves to "Disconnected"

### After Fix

- ✅ Child locks immediately show "Disconnected" status for disabled parent slots
- ✅ No sync loops - proper status displayed
- ✅ No unnecessary Z-Wave traffic after initial sync
- ✅ Parent/child synchronization works correctly for active slots
- ✅ Debug logs: `parent=None (actual=5979, enabled=False) child=None mismatch=False`
- ✅ Physical testing: Active PINs still work correctly on all locks

### Performance Improvements

- **Before**: 50+ Z-Wave clear commands over 10 minutes for disabled slots
- **After**: 0 unnecessary commands - proper sync status maintained
- **Before**: Infinite retry loops continuing indefinitely
- **After**: Clean sync with correct status display

## Type of change

- [ ] Dependency upgrade
- [x] Bugfix (non-breaking change which fixes an issue)
- [ ] New feature (which adds functionality)
- [ ] Breaking change (fix/feature causing existing functionality to break)
- [ ] Code quality improvements to existing code or addition of tests

## Additional information

- This PR fixes or closes issue: fixes #520
- This PR is related to issue: Related to PR #515 (merged Nov 7, 2025)

### Affected Hardware

- **Primarily**: Schlage BE469 (and other BE-series) in parent-child configurations
- **Potentially**: Any lock brand using parent-child sync with disabled slots

### Safe for Other Locks

Changes are defensive and only affect the comparison logic:

1. **Disabled slot check**: Only modifies comparison when `enabled=False` or `active=False`
2. **No Z-Wave command changes**: Only affects when mismatch is detected
3. **Preserves active slot sync**: Enabled/active slots continue syncing normally

### Side Benefit

Also fixes sync loops when parent slots become inactive due to time/date restrictions while still having a PIN configured. The same logic applies: if the parent slot isn't currently active, it should be treated as having no PIN for child sync comparison.

### Target Branch

`beta` (for inclusion in next release)

### Related to PR #515

**PR #515** (merged Nov 7, 2025): Fixed Schlage masked response sync issues

- Issue: Locks return masked PINs (`**********`) causing sync loops
- Fix: Handle masked responses and update child PIN in memory

**This PR** (new): Fixes disabled parent slot sync loop

- Issue: Disabled parent slots with stale PIN values cause infinite clears
- Fix: Treat disabled/inactive parent slots as having `pin=None`

Both PRs modify the same `_update_child_code_slots()` method but address different root causes. PR #515 handled the case where locks mask their responses; this PR handles the case where parent slots are disabled but retain PIN values.
