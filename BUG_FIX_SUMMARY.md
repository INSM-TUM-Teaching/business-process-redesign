# Bug Fix: OR Dependency Lock Violation Not Detected

## Problem Statement

The BPMN hardcoded UI demo has a locked OR dependency between activities 'h' and 'i', meaning at least one of them must occur in every process instance. BPMN Operation 1 (Insert activity 'c') was incorrectly succeeding when it should have been blocked because it creates a trace `['a', 'c']` where neither 'h' nor 'i' occurs, violating the OR constraint.

## Root Causes

### 1. Incorrect Hardcoded Variant
**File:** `change_operations/insert_operation.py:88-91`

The hardcoded variant for BPMN Operation 1 was `['a', 'c', 'h']`, which includes 'h' and thus satisfies the h∨i OR constraint. However, the operation description states "the process ends as soon as c is executed," which should create a trace `['a', 'c']` without h, i, or j.

**Fix:** Changed the hardcoded variant from `['a', 'c', 'h']` to `['a', 'c']`.

### 2. Inadequate Lock Validation
**File:** `utils/lock_dependencies_violations.py`

The lock validation only checked if the dependency **relationship** (matrix structure) remained unchanged, but didn't verify whether the dependency **constraint** (semantic meaning) was satisfied in all acceptance sequences.

For example, an OR dependency might still exist in the matrix (h→i shows OR relationship), but if the operation creates traces where neither 'h' nor 'i' occurs, the OR constraint (h∨i) is violated in those traces.

**Fix:** Added `_check_existential_constraint_in_sequences()` function that:
- Generates all acceptance sequences from the modified matrix
- Validates that each sequence satisfies the locked existential constraint
- Returns False if any sequence violates the constraint

Updated both `locked_dependencies_preserved()` and `get_violated_locked_dependencies()` to use this sequence-level validation.

### 3. Duplicate Lock Validation in Flask App
**File:** `app.py:671-715`

The Flask app had its own simplified lock validation logic that only checked matrix-level changes, not sequence-level constraint satisfaction. It wasn't using the proper utility function.

**Fix:** Replaced the duplicate validation logic with calls to `locked_dependencies_preserved()` and `get_violated_locked_dependencies()` from the utils module.

### 4. Missing Lock in BPMN_LOCKS
**File:** `app.py:34-39`

The BPMN_LOCKS definition was missing the lock on `b→e` temporal dependency that exists in `static/app.js`.

**Fix:** Added `{'from': 'b', 'to': 'e', 'temporal': True, 'existential': False}` to BPMN_LOCKS.

## Changes Made

### 1. `utils/lock_dependencies_violations.py`
- **Added import:** `from constraint_logic import check_existential_relationship`
- **Added function:** `_check_existential_constraint_in_sequences()` - Validates existential constraints in all acceptance sequences
- **Updated function:** `locked_dependencies_preserved()` - Now performs sequence-level validation for locked existential dependencies
- **Updated function:** `get_violated_locked_dependencies()` - Now detects sequence-level violations

### 2. `change_operations/insert_operation.py`
- **Line 90-91:** Changed hardcoded variant from `['a', 'c', 'h']` to `['a', 'c']`
- **Added comment:** Clarified that the process "ends after c (early termination)"

### 3. `app.py`
- **Line 26:** Added import of `locked_dependencies_preserved` and `get_violated_locked_dependencies`
- **Line 38:** Added missing lock `{'from': 'b', 'to': 'e', 'temporal': True, 'existential': False}`
- **Lines 671-715:** Replaced custom lock validation logic with proper utility function calls
- **Improved error messages:** Now provides detailed information about which constraints were violated

### 4. `docs/static/app.js`
- Synced with `static/app.js` to ensure consistency

### 5. `tests/test_lock_or_dependency.py`
- Created comprehensive test to verify OR dependency lock validation

## Expected Behavior After Fix

When attempting BPMN Operation 1 (Insert activity 'c') with the locked OR dependency between 'h' and 'i':

1. The operation will create a modified matrix with the trace `['a', 'c']`
2. The lock validation will detect that this trace violates the h∨i OR constraint
3. The operation will be **rejected** with an error message:
   ```
   "Existential dependency from 'h' to 'i' is locked and was violated.
    This operation would create process instances that don't satisfy the constraint."
   ```

## Technical Details

### What is an OR Existential Dependency?
An OR dependency between activities 'h' and 'i' (h∨i) means: **At least one of 'h' or 'i' must occur in every process instance.**

Valid traces:
- `['a', 'b', 'h']` - ✓ contains h
- `['a', 'b', 'i', 'j']` - ✓ contains i
- `['a', 'b', 'h', 'i', 'j']` - ✓ contains both

Invalid trace:
- `['a', 'c']` - ✗ contains neither h nor i

### Why Matrix-Level Validation is Insufficient
The adjacency matrix represents relationships between activities, but doesn't capture all possible execution paths. An operation might preserve the h→i relationship in the matrix while creating execution paths that violate the constraint.

For OR dependencies specifically:
- **Matrix level:** h→i shows OR relationship (relationship exists)
- **Sequence level:** All traces must have at least one of h or i (constraint satisfied)

Both levels must be validated for correctness.

## Files Modified

1. `utils/lock_dependencies_violations.py` - Enhanced lock validation logic
2. `change_operations/insert_operation.py` - Fixed hardcoded variant
3. `app.py` - Updated lock validation and added missing lock
4. `docs/static/app.js` - Synced with static/app.js
5. `tests/test_lock_or_dependency.py` - New test file
6. `test_fix.py` - Manual test script

## Testing the Fix

The Flask server needs to be restarted to pick up the code changes:

```bash
# Restart the Flask server
pkill -f "python.*run.py"  # Kill existing server if running
python run.py              # Start server with new code
```

Then navigate to `http://127.0.0.1:5000` and try BPMN Operation 1. It should now be **rejected** with an error message about violating the locked h→i OR dependency.
