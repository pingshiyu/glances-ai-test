# Timer and Counter – Working semantics

Component: `glances/timer.py` – class `Timer` and class `Counter`.

This document is a copy of the initial semantics; update only when refining after crashes or precondition fixes (Steps 2–3).

---

## Abstract state

### Timer

- **duration:** Float (seconds). Set by constructor, `set(duration)`, or `reset(duration=...)`.
- **target:** Time (float, from `time.time()`) at which the timer is considered finished. Invariant: after `start()` or `reset()`, `target = time() + duration`.

### Counter

- **target:** Datetime (from `datetime.now()`) stored at last `start()` or `reset()`. Elapsed time = `(datetime.now() - target).total_seconds()`.

---

## Public API

### Timer

#### Constructor `Timer(duration)`

- **Preconditions:** `duration` must be numeric (int or float). The implementation does not validate.
- **Postconditions:** `self.duration = duration`; calls `start()`, so `target = time() + duration`.
- **Higher-order:** No.

#### `set(duration)`

- **Preconditions:** `duration` must be numeric (int or float).
- **Postconditions:** `self.duration = duration`. `target` is unchanged until next `start()` or `reset()`.
- **Higher-order:** No.

#### `reset(duration=None)`

- **Preconditions:** If `duration` is not `None`, it must be numeric.
- **Postconditions:** If `duration is not None`, same as `set(duration)` then `start()`. Otherwise, same as `start()` (restart with current duration). So after the call, `target = time() + self.duration`.
- **Higher-order:** No.

#### `start()`

- **Preconditions:** None.
- **Postconditions:** `target = time() + self.duration`.
- **Higher-order:** No.

#### `get()`

- **Preconditions:** None.
- **Postconditions:** Returns `self.duration - (self.target - time())`. Can be negative after the timer has passed its target.
- **Higher-order:** No.

#### `finished()`

- **Preconditions:** None.
- **Postconditions:** Returns `time() > self.target`.
- **Higher-order:** No.

### Counter

#### Constructor `Counter()`

- **Preconditions:** None.
- **Postconditions:** Calls `start()`, so `target = datetime.now()`.
- **Higher-order:** No.

#### `start()`

- **Preconditions:** None.
- **Postconditions:** `target = datetime.now()`.
- **Higher-order:** No.

#### `reset()`

- **Preconditions:** None.
- **Postconditions:** Same as `start()`: `target = datetime.now()`.
- **Higher-order:** No.

#### `get()`

- **Preconditions:** None.
- **Postconditions:** Returns `(datetime.now() - self.target).total_seconds()` (non-negative float).
- **Higher-order:** No.

---

## Higher-order functions

None in this API.
