# GlancesAttribute – Initial semantics (fixed)

Component: `glances/attribute.py` – class `GlancesAttribute`.

This document is fixed after Step 1 and must not be changed.

---

## Abstract state

- **L:** Length of `_history`: the number of `(datetime, value)` tuples stored. When `_history_max_size` is `None`, the implementation never appends to `_history` (only the `if self._history_max_size:` branch runs the append). So for history to grow, `_history_max_size` must be set to a positive integer.
- **_value:** The last stored pair `(timestamp, value)`; set by the value setter and used by the value getter.
- **_history_max_size:** Optional cap; when set, `history_add` (and the value setter) append and may pop from the front when at capacity.

---

## Public API

### Constructor `GlancesAttribute(name, description='', history_max_size=None)`

- **Preconditions:** None.
- **Postconditions:** New attribute with empty `_history`, `_value` None. If `history_max_size` is set, subsequent `history_add` / value setter will append; if `None`, they will not append (implementation detail).
- **Higher-order:** No.

### `value` (setter)

- **Preconditions:** None. Accepts any scalar.
- **Postconditions:** `_value` is set to `(datetime.now(UTC), new_value)`. If `_history_max_size` is set, that pair is appended to `_history` (and possibly one element is removed from the front if at max size). If `_history_max_size` is `None`, the implementation does not append.
- **Higher-order:** No.

### `value` (getter)

- **Preconditions:** `L >= 2` and the last two entries have different timestamps (else division by zero). The implementation uses the last entry and the one before it.
- **Postconditions:** Returns rate `(last[1] - prev[1]) / (last[0] - prev[0])`, or `None` if `L == 0`. No side effects.
- **Higher-order:** No.

### `history_add(value)`

- **Preconditions:** `value` should be a tuple `(timestamp, val)` for consistency. If `_history_max_size` is set, the entry is appended (with possible pop from front); if `None`, the implementation does not append.
- **Postconditions:** When `_history_max_size` is set, `_history` has one more entry (or same length if at cap and one was removed). No effect when `_history_max_size` is `None`.
- **Higher-order:** No.

### `history_reset()`

- **Preconditions:** None.
- **Postconditions:** `_history` is empty. No other state change.
- **Higher-order:** No.

### `history_len()` / `history_size()`

- **Preconditions:** None.
- **Postconditions:** Returns `len(_history)`. No side effects.
- **Higher-order:** No.

### `history_raw(nb=0)`

- **Preconditions:** `nb >= 0`. Slicing `_history[-nb:]` is safe for any `nb`.
- **Postconditions:** Returns `_history[-nb:]`. No side effects.
- **Higher-order:** No.

### `history_json(nb=0)`

- **Preconditions:** `nb >= 0`.
- **Postconditions:** Returns list of `(isoformat(timestamp), value)` for `_history[-nb:]`. No side effects.
- **Higher-order:** No.

### `history_value(pos=1)`

- **Preconditions:** `1 <= pos <= L`; else `IndexError` (uses `_history[-pos]`).
- **Postconditions:** Returns `_history[-pos]`. No side effects.
- **Higher-order:** No.

### `history_mean(nb=5)`

- **Preconditions:** `L >= 1` for `zip(*self._history)`. The implementation divides by `float(v[-1] - v[-nb])` (known bug: denominator should be count, not value difference). Also **ZeroDivisionError** when `v[-1] == v[-nb]` (e.g. constant values).
- **Postconditions:** Returns the (currently buggy) “mean” as implemented. No side effects.
- **Higher-order:** No.

---

## Higher-order functions

None in this API.
