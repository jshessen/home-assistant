# Fix: Parent-Child Lock Sync Loop When Parent Slot is Disabled

## Issue

Fixes #520 - Slots stuck in "Adding" or "Deleting" status

## Problem Description

When a parent lock has a code slot **disabled** (but the PIN text field still contains a value), child locks get stuck in an infinite sync loop with "Deleting" status. This occurs because:

1. User disables a code slot on the parent lock
2. Child locks successfully clear the PIN (confirmed at Z-Wave level)
3. Sync logic compares:
   - Parent PIN: `"5979"` (still in memory from text field, even though disabled)
   - Child PIN: `None` (successfully cleared)
   - Result: **Mismatch detected** → Try to clear again
4. Loop repeats every 15 seconds, causing:
   - Z-Wave controller saturation
   - Child locks stuck showing "Deleting" status indefinitely
   - Excessive Z-Wave traffic

## Root Cause

In `coordinator.py`, the `_update_child_code_slots()` method compares parent and child PINs directly without considering whether the parent slot is enabled/active. A disabled parent slot should be treated as having no PIN for comparison purposes.

**Problematic code (line ~2161):**

```python
child_pin = child_kmlock.code_slots[code_slot_num].pin
pin_mismatch = kmslot.pin != child_pin and not (
    child_pin and "*" in child_pin
)
```

This compares the actual PIN value stored in the parent slot, even when the slot is disabled.

## Solution

Treat disabled or inactive parent slots as having `pin=None` for comparison purposes. This prevents false mismatch detection when a parent slot is disabled but still has a PIN value in memory.

**Fixed code (lines 2155-2165):**

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
```

## Testing

Tested with:

- **Locks**: 4x Schlage BE469 (1 parent, 3 children)
- **Z-Wave**: Z-Wave JS UI
- **Scenario**:
  1. Disabled code slot 1 on parent lock (PIN text field still contained "5979")
  2. Child locks were already cleared at Z-Wave level
  3. **Before fix**: Child locks stuck in "Deleting" status, sync loop every 15 seconds
  4. **After fix**: Child locks immediately show "Disconnected" status, no sync loop

### Verification

- ✅ No more infinite sync loops
- ✅ Child locks show "Disconnected" status for disabled slots
- ✅ Z-Wave logs show no excessive traffic
- ✅ No errors in Home Assistant logs
- ✅ Slots with active PINs continue to sync correctly

## Files Changed

- `custom_components/keymaster/coordinator.py` (lines 2155-2165)

## Additional Notes

This fix also addresses the scenario where parent slots become inactive due to time/date restrictions while still having a PIN configured. The same logic applies: if the parent slot isn't currently active, it should be treated as having no PIN for child sync comparison.

## Workaround (until merged)

Users can apply this patch manually to their local keymaster installation by modifying `coordinator.py` in the `_update_child_code_slots()` method.
