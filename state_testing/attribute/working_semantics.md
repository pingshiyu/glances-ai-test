# GlancesAttribute – Working semantics

Component: `glances/attribute.py` – class `GlancesAttribute`.

This document is a copy of the initial semantics and may be updated when refining pre/postconditions or documenting crashes.

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
- **Postconditions:** Returns the (currently buggy) "mean" as implemented. No side effects.
- **Higher-order:** No.

---

## Higher-order functions

None in this API.

---

## Crashes (to be filled when iterating)

1. **history_mean(nb)** – **API bug.** ZeroDivisionError when `v[-1] == v[-nb]` (constant values in the slice). Implementation also uses wrong denominator (value difference instead of count). Executor commented out; see state_testing/attribute/attribute_glances_lib.py.
2. **value** (getter) – **API bug.** TypeError: unsupported operand type(s) for /: 'int' and 'datetime.timedelta'. The implementation divides a numeric difference by a timedelta; Python 3 does not support that. Also, when only history_add was used (no value setter), _value is None and the getter crashes with NoneType not subscriptable. Executor commented out.

---

## Impact on the main program (investigation)

**Conclusion: the two bugs do not currently cause crashes in the real application**, because the code paths that would trigger them are not used.

### How GlancesAttribute is used in production

- **Creation/update:** `GlancesHistory.add(key, value, ...)` creates or reuses a `GlancesAttribute` and always updates it via the **setter** only: `self.stats_history[key].value = value`. So `_value` is always set and `_history` is only extended through the setter (which calls `history_add(self._value)`). No code path uses **only** `history_add` without the setter.
- **Reading history:** Callers use `stats_history.get(nb=nb)` or `get_json(nb=nb)`, which call `history_raw(nb)` and `history_json(nb)` on each attribute. The **value getter** and **history_mean** are never called in the main codebase.

### Bug 1: history_mean

- **Where it could crash:** ZeroDivisionError when the last `nb` values are all equal; also the formula is wrong (denominator uses value difference instead of count).
- **Real-world impact:** **None.** No plugin or export calls `history_mean()`. The only use is in `tests/test_core.py` (`test_097_attribute`), which asserts `a.history_mean(nb=3) == 4.5` for values 2,3,4 — the current (buggy) formula happens to yield 4.5 for that input, so the test is asserting buggy behaviour. Fixing the implementation would break that test until it is updated.

### Bug 2: value getter

- **Where it could crash:** (a) `TypeError` when dividing a number by a `timedelta` (e.g. if `_value` is not the last history entry); (b) `TypeError: 'NoneType' object is not subscriptable` when `_value` is `None` (only `history_add` used).
- **Real-world impact:** **None** for the current design. The application only updates attributes via the setter and only reads via `history_raw` / `history_json`. So the getter is never invoked in normal flow.
- **Theoretical risk:** `GlancesAttribute.__repr__` and `__str__` both delegate to `self.value` (the getter). So **any** code that stringifies an attribute (e.g. `str(attr)`, `repr(attr)`, logging, or f-strings) would invoke the getter and could hit one of the crashes. Today no such path exists: attribute objects are not passed to formatting or logging; only the results of `get()` / `get_json()` (lists/dicts) are used.

### Recommendation

- The main program is safe as long as it continues to use only the setter and `history_raw` / `history_json`. No change is strictly required for correctness in production.
- Fixing the API is still advisable for: (1) correctness of `history_mean` and the value getter if they are ever used or exposed; (2) avoiding latent bugs if future code stringifies attributes or calls the getter/`history_mean`; (3) aligning the unit test with intended semantics instead of the current buggy behaviour.

---

## Fuzzer design

**Layout:** All files live under `state_testing/attribute/`:

- `attribute_glances_generators.py` – Stateless: `gen_value_for_setter`, `gen_history_entry`, `gen_nb`. Stateful factories: `gen_pos(attr)`, `gen_nb_mean(attr)` returning no-arg callables (used only when L>=1). Values include int/float, zero, negative; nb is non-negative.
- `attribute_glances_lib.py` – `get_executors(attr)` returns a list of `(min_history, require_value_set, executor)`. min_history is 0, 1, or 2. require_value_set is True only for the value getter (so we only run it when `attr._value` is not None). Executors: value setter, history_add, history_reset, history_raw, history_json, history_value, history_len. history_mean and value getter are commented out due to API bugs.
- `attribute_glances_entry.py` – `dummyTester()` creates one `GlancesAttribute("fuzz", description="", history_max_size=100)` (history_max_size must be set so that value setter and history_add actually append). Gets executors, then 1000 iterations: filter candidates by `attr.history_len() >= mh` and `not require_value_set or attr._value is not None`, then `random.choice(candidates)()`.

**Design decisions:**

1. **Single shared instance** – One `GlancesAttribute` in `dummyTester`; all executors close over it.
2. **history_max_size set** – The implementation only appends to _history when `_history_max_size` is truthy; we use 100 so that add/setter grow history.
3. **Precondition filtering** – Executors are tagged with (min_history, require_value_set). Each iteration we only run executors whose preconditions hold (L >= min_history and, if require_value_set, _value is not None).
4. **No try/except** – Preconditions are enforced by construction and filtering.
5. **history_mean and value getter** – Commented out and documented as API bugs; fuzzer succeeds for 1000 iterations without them.

**Success criterion:** Running `python -m state_testing.attribute.attribute_glances_entry` (or calling `dummyTester()`) completes 1000 iterations with no errors. Verified.
