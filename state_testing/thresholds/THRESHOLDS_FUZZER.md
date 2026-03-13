# GlancesThresholds fuzzer: structure and design

This document describes the state-based fuzzer for **glances/thresholds.py** (GlancesThresholds), so another agent or a human can understand how it was implemented and reimplement or extend it without repeating common mistakes.

---

## Overview

The fuzzer drives the public API of `GlancesThresholds` with random inputs over 1000 iterations. It uses the state_testing framework (`make_executor`, generators) and does **not** use try/except to absorb errors: preconditions are enforced by generators so that valid inputs are produced.

---

## File roles

| File | Role |
|------|------|
| **thresholds_glances_entry.py** | Entry point. Sets `XDG_CACHE_HOME` so Glances logger writes under the project, then creates one `GlancesThresholds()` instance, builds the executor list, and runs 1000 iterations: each iteration picks a random executor and runs it. Defines `dummyTester()`. |
| **thresholds_glances_lib.py** | Defines `get_executors(sut)`. Returns a list of callables; each callable is an executor that runs one or more generators and calls one API method on `sut` with the generated arguments. |
| **thresholds_glances_generators.py** | No-arg generator callables that return values satisfying the API preconditions. Used by the lib to build executors. |
| **initial_semantics.md** | Fixed specification (never edit after Step 1): abstract state, pre/postconditions for `add` and `get`. |
| **working_semantics.md** | Copy of initial semantics; update only when refining after crashes or findings. |

---

## Design decisions

1. **Single SUT instance**  
   One `GlancesThresholds()` is shared by all executors so that random sequences of `add` and `get` exercise stateful behaviour (e.g. many adds, then get with known/unknown keys).

2. **No precondition filtering in the entry point**  
   Unlike the attribute fuzzer (which filters by `history_len` and `_value`), this fuzzer does not filter which executors are eligible each iteration. Both `get(stat_name)` and `add(stat_name, threshold_description)` are safe for any `stat_name`/`None` as long as `threshold_description` is one of the four valid strings. So we only need generators to satisfy that precondition.

3. **Only valid threshold descriptions for `add()`**  
   `add()` returns `False` and does not modify state if `threshold_description not in ['OK','CAREFUL','WARNING','CRITICAL']`. The check uses **exact case** (no `.capitalize()` on the input in the check). So `gen_threshold_description()` returns only those four strings. This avoids crashes and ensures we exercise the success path.

4. **`gen_stat_name_or_none()` for `get()`**  
   `get(stat_name=None)` is total: `None` returns the full dict, any string returns either the threshold instance or `{}`. The generator returns `None` with some probability and otherwise a stat name (including empty string and unknown keys) to cover “get all”, “get one (known)”, and “get one (missing)”.

5. **Logger and environment**  
   Importing `glances.thresholds` triggers the package root, which configures the Glances logger and writes to a file. To avoid permission errors when the default log path is not writable, the entry point sets `XDG_CACHE_HOME` to a directory under the project (`.cache`) **before** importing Glances, and ensures that directory exists.

---

## How to run

From the **project root**, with the SUT environment activated (see `state_testing/README.md`):

```bash
# Create/activate SUT venv if needed
python -m venv .venv-sut && source .venv-sut/bin/activate
pip install -e .

# Run the fuzzer (1000 iterations)
python -m state_testing.thresholds.thresholds_glances_entry
```

Or call `dummyTester()` from that module. Success criterion: the loop completes 1000 iterations without errors.

---

## Executors

- **Executor 1 – `add`:** Generators `[gen_stat_name, gen_threshold_description]`. Calls `sut.add(stat_name, threshold_description)`.
- **Executor 2 – `get`:** Generator `[gen_stat_name_or_none]`. Calls `sut.get(stat_name)`.

No executors are commented out; no API bugs were found during development.

---

## Pitfalls and reimplementation notes

- **Exact casing:** The API accepts only `'OK'`, `'CAREFUL'`, `'WARNING'`, `'CRITICAL'`. Do not generate `'ok'`, `'careful'`, etc., or `add()` will return `False` and you might be tempted to treat that as a crash; the fuzzer is designed to avoid that by generating only valid descriptions.
- **Import order:** Set `XDG_CACHE_HOME` (and create the directory) before any `from glances...` import, or the logger may try to write to a non-writable path and raise.
- **SUT environment:** Run with a venv that has `pip install -e .` so that `glances` and `psutil` are available; otherwise import fails.
- **No try/except:** Do not wrap executor calls in try/except to hide failures; fix preconditions in the generators or document API bugs and comment out the executor.
