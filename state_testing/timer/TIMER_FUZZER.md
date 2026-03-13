# Timer and Counter fuzzer: structure and design

This document describes the state-based fuzzer for **glances/timer.py** (Timer and Counter), so another agent or a human can understand how it was implemented and reimplement or extend it without repeating common mistakes.

---

## Overview

The fuzzer drives the public API of `Timer` and `Counter` with random inputs over 1000 iterations. It uses the state_testing framework (`make_executor`, generators) and **mocks time** so that behaviour is deterministic: `time.time()` and `datetime.now()` are patched at `glances.timer` to read from a logical time that the entry point resets each iteration and that some executors advance before calling `get()` or `finished()`. The fuzzer does not use try/except to absorb errors; preconditions are enforced by generators.

---

## File roles

| File | Role |
|------|------|
| **timer_glances_entry.py** | Entry point. Sets `XDG_CACHE_HOME` before any glances import, installs patches for `glances.timer.time` and `glances.timer.datetime`, creates one `Timer(gen_duration())` and one `Counter()`, builds the executor list, and runs 1000 iterations: each iteration sets logical time to 1000.0, picks a random executor, and runs it. Defines `dummyTester()`. |
| **timer_glances_lib.py** | Defines `get_executors(sut_timer, sut_counter, logical_time_list)` and `_make_fake_datetime(time_getter)`. Returns a list of callables; each callable is an executor that runs zero or more generators and calls one API method on the timer or counter. Advance-time executors increment `logical_time_list[0]` by a generated delta then call `get()` or `finished()`. |
| **timer_glances_generators.py** | No-arg generator callables: `gen_duration()`, `gen_duration_or_none()`, `gen_time_delta()`. They return values satisfying API preconditions (numeric duration, optional duration for reset, positive seconds for time advance). |
| **initial_semantics.md** | Fixed specification (never edit after Step 1): abstract state and pre/postconditions for Timer and Counter. |
| **working_semantics.md** | Copy of initial semantics; update only when refining after crashes or findings. |

---

## Design decisions

1. **Time mocking (Option A)**  
   `glances.timer.time` is patched with a callable that returns `logical_time[0]`. `glances.timer.datetime` is patched with a fake type whose `now()` returns `datetime.fromtimestamp(logical_time[0])`, so Timer and Counter see a single logical clock. The entry point resets `logical_time[0] = 1000.0` at the start of each of the 1000 iterations so that each executor run starts from a known time.

2. **One Timer and one Counter**  
   A single shared `Timer` and `Counter` are created inside the patch context (so their use of `time()` and `datetime.now()` is already mocked). All executors operate on these two instances so that random sequences exercise stateful behaviour.

3. **Patch before creating SUT**  
   The entry point installs the patches first, then does `from glances.timer import Timer, Counter` and constructs the instances. Thus when `Timer.__init__` calls `start()`, which calls `time()`, the patched `time` is used.

4. **Advance-time executors**  
   Two executors advance logical time by a generated delta and then call `sut_timer.get()` or `sut_timer.finished()`. This exercises the “timer expired” path (negative remaining time, `finished()` True) without relying on real wall-clock time.

5. **Duration generators**  
   `gen_duration()` returns non-negative int or float (edge cases 0, 1, 2, 5, 10, 60, 100, 3600 plus random values in [0, 100]). `gen_duration_or_none()` returns `None` about 40% of the time and otherwise `gen_duration()` for `reset(duration=None)`.

6. **Logger and environment**  
   The entry point sets `XDG_CACHE_HOME` to a directory under the project (`.cache`) before importing Glances, for consistency with other fuzzers. The SUT environment (venv with `pip install -e .`) is required because `import glances.timer` loads the package root, which checks for `psutil` and exits if missing.

---

## How to run

From the **project root**, with the SUT environment activated (see `state_testing/README.md`):

```bash
# Create/activate SUT venv if needed
python -m venv .venv-sut && source .venv-sut/bin/activate
pip install -e .

# Run the fuzzer (1000 iterations)
python -m state_testing.timer.timer_glances_entry
```

Or call `dummyTester()` from that module. Success criterion: the loop completes 1000 iterations without errors.

---

## Executors

**Timer (shared instance):**

- **set(duration):** Generator `[gen_duration]`. Sets timer duration.
- **reset(duration=None):** Generator `[gen_duration_or_none]`. Resets and optionally sets new duration.
- **start():** No generators. Restarts the timer with current duration.
- **get():** No generators. Returns remaining time (may be negative).
- **finished():** No generators. Returns whether the timer has passed its target.
- **advance then get:** Generator `[gen_time_delta]`. Advances logical time by delta, then returns `get()`.
- **advance then finished:** Generator `[gen_time_delta]`. Advances logical time by delta, then returns `finished()`.

**Counter (shared instance):**

- **start():** No generators. Sets counter target to “now”.
- **reset():** No generators. Same as start.
- **get():** No generators. Returns elapsed seconds since target.

No executors are commented out; no API bugs were found during development.

---

## Pitfalls and reimplementation notes

- **Timer.get() can be negative:** After the logical time passes the timer’s target, `get()` returns a negative value. The implementation does not clamp; the fuzzer accepts this.
- **Patch at `glances.timer`:** Patch `glances.timer.time` and `glances.timer.datetime`, not `time` or `datetime` at the top level, so that the module under test sees the mocks.
- **Counter uses datetime, Timer uses time:** Both must be mocked for a single logical clock; we use one float and `datetime.fromtimestamp(logical_time[0])` for `datetime.now()`.
- **SUT environment required:** The Glances package root checks for `psutil` on import; run with a venv that has the project installed (`pip install -e .`).
- **No try/except:** Do not wrap executor calls in try/except to hide failures; fix preconditions in the generators or document API bugs and comment out the executor.
