# GlancesThresholds – Initial semantics (fixed)

Component: `glances/thresholds.py` – class `GlancesThresholds`.

This document is fixed after Step 1 and must not be changed.

---

## Abstract state

- **State:** A mapping from `stat_name` (string) to threshold description, where the description is one of `'OK'`, `'CAREFUL'`, `'WARNING'`, `'CRITICAL'`. Initially the map is empty. The concrete implementation stores for each key an instance of `GlancesThresholdOk`, `GlancesThresholdCareful`, `GlancesThresholdWarning`, or `GlancesThresholdCritical` respectively.

---

## Public API

### `add(stat_name, threshold_description)`

- **Preconditions:** `threshold_description` must be exactly one of `['OK', 'CAREFUL', 'WARNING', 'CRITICAL']` (exact case). The implementation checks `threshold_description not in self.threshold_list` and returns `False` without modifying state if the condition is violated.
- **Postconditions:** If the precondition holds, the abstract state maps `stat_name` to `threshold_description` (and the concrete `_thresholds[stat_name]` is set to the corresponding threshold instance). Returns `True`. If the precondition is violated, state is unchanged and the method returns `False`.
- **Higher-order:** No.

### `get(stat_name=None)`

- **Preconditions:** None. `stat_name` may be any value (typically `None` or a string).
- **Postconditions:** If `stat_name is None`, returns the full `_thresholds` dict (all stat names to threshold instances). If `stat_name` is not `None` and is a key in the abstract state, returns the corresponding threshold instance. If `stat_name` is not `None` and is not a key, returns `{}`. No side effects.
- **Higher-order:** No.

---

## Higher-order functions

None in this API.
