# GlancesHistory – Working semantics

Component: `glances/history.py` – class `GlancesHistory`.

This document is a copy of the initial semantics and may be updated when refining pre/postconditions or documenting crashes.

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

---

## Crashes (to be filled when iterating)

(No crashes recorded yet.)

---

## Fuzzer design

**Layout:** All files live under `state_testing/history/`:

- `_glances_loader.py` – Loads `glances.attribute` and `glances.history` via `importlib` without running `glances/__init__.py`, so the fuzzer runs without psutil.
- `history_glances_generators.py` – No-arg generator callables: `gen_key`, `gen_value`, `gen_description`, `gen_history_max_size`, `gen_nb`. Keys include empty string and short alphanumeric; values include int/float/zero/negative; `nb` is non-negative only.
- `history_glances_lib.py` – `get_executors(history)` returns a list of four executors (add, reset, get, get_json), each built with `make_executor(generators, func)` from `state_testing.executor`. The shared `GlancesHistory` instance is closed over in the lambdas.
- `history_glances_entry.py` – `dummyTester()` creates one `GlancesHistory()`, gets executors, then runs 1000 iterations of `random.choice(executors)()`.

**Design decisions:**

1. **Single shared instance:** One `GlancesHistory()` is created in `dummyTester()` and passed to `get_executors(history)` so that random sequences of add/reset/get/get_json exercise stateful behaviour on the same object.
2. **No try/except:** Generators satisfy preconditions by construction (e.g. `gen_nb()` returns only non-negative ints); we do not catch exceptions to avoid crashes.
3. **Loader to avoid psutil:** The main `glances` package runs a psutil check and `sys.exit(1)` on import. The fuzzer uses `_glances_loader` to load only `glances/attribute.py` and `glances/history.py` so it can run in environments where psutil is not installed (e.g. as stated in state_testing README).
4. **Abstract state:** We do not maintain an explicit abstract state mirror in code; the semantics document describes it. If we needed precondition-aware generators (e.g. restrict `get(nb)` to `nb <= min history length`), we would add a class holding the shared history and a key set / per-key counts and pass that into generator factories.

**Success criterion:** Running `python -m state_testing.history.history_glances_entry` (or calling `dummyTester()`) completes 1000 iterations with no errors. Verified.
