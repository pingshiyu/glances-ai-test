# GlancesHistory – Initial semantics (fixed)

Component: `glances/history.py` – class `GlancesHistory`.

This document is fixed after Step 1 and must not be changed.

---

## Abstract state

- **Keys:** The set of keys (strings) that have been passed to `add()` at least once. Equivalently, the keys present in `stats_history`. After `reset()`, keys remain but each attribute's history list is empty.

---

## Public API

### `add(key, value, description='', history_max_size=None)`

- **Preconditions:** None enforced by the implementation. The API accepts any `key` (used as dict key and passed to `GlancesAttribute`), any `value` (stored with timestamp by the attribute), any `description` string, and `history_max_size` either `None` or an integer.
- **Postconditions:** After the call, `key` is in `stats_history`. The attribute at `key` has one more entry in its history (the current value was appended with a timestamp).
- **Higher-order:** No.

### `reset()`

- **Preconditions:** None.
- **Postconditions:** For every key in `stats_history`, the corresponding attribute's history list is empty. The set of keys is unchanged.
- **Higher-order:** No.

### `get(nb=0)`

- **Preconditions:** `nb >= 0` (used as slice index in `_history[-nb:]`).
- **Postconditions:** Returns a dict mapping each key in `stats_history` to the list of the last `nb` history entries (raw tuples). If `nb == 0`, returns the last 0 elements (empty list) per key. No side effects.
- **Higher-order:** No.

### `get_json(nb=0)`

- **Preconditions:** `nb >= 0`.
- **Postconditions:** Same as `get(nb)` but each list entry is (isoformat date string, value). No side effects.
- **Higher-order:** No.

---

## Higher-order functions

None in this API.
