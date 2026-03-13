# GlancesFilterList fuzzer: structure and design

This document describes the state-based fuzzer for **glances/filter.py** (GlancesFilterList / GlancesFilter), so another agent or a human can understand how it was implemented and reimplement or extend it without repeating common mistakes.

---

## Overview

The fuzzer drives the public API of `GlancesFilterList` with random inputs over 1000 iterations. It uses the state_testing framework (`make_executor`, generators) and does **not** use try/except to absorb errors: preconditions are enforced by generators so that valid inputs are produced.

---

## File roles

| File | Role |
|------|------|
| **filter_glances_entry.py** | Entry point. Sets `XDG_CACHE_HOME` so Glances logger writes under the project, then creates one `GlancesFilterList()` instance, builds the executor list, and runs 1000 iterations: each iteration picks a random executor and runs it. Defines `dummyTester()`. |
| **filter_glances_lib.py** | Defines `get_executors(sut)`. Returns a list of callables; each callable is an executor that runs zero or more generators and calls one API method on `sut` with the generated arguments. |
| **filter_glances_generators.py** | No-arg generator callables that return values satisfying the API preconditions. Used by the lib to build executors. |
| **initial_semantics.md** | Fixed specification (never edit after Step 1): abstract state, pre/postconditions for filter setter/getter and `is_filtered`. |
| **working_semantics.md** | Copy of initial semantics; update only when refining after crashes or findings. |

---

## Design decisions

1. **Single SUT instance**  
   One `GlancesFilterList()` is shared by all executors so that random sequences of filter setter, getter, and `is_filtered` exercise stateful behaviour (growing list of filters, then querying with various process dicts).

2. **No precondition filtering in the entry point**  
   All three executors (set filter, get filter, is_filtered) are safe to call at any time. The filter setter accepts any string; the getter takes no args; `is_filtered` tolerates any dict (missing keys / None values yield False). So we do not filter which executors are eligible per iteration.

3. **Only compilable regex segments for the filter setter**  
   The filter setter splits the string on `,` and passes each segment to a `GlancesFilter`. If a segment fails to compile as a regex, that filter becomes inactive (no exception). To keep abstract state predictable and avoid relying on try/except, `gen_filter_string()` produces only segments that compile: a fixed set of safe patterns (e.g. `.*`, `python`, `username:nicolargo`) plus short random fragments built from safe characters (alphanumeric, `.`, `*`). We do not generate invalid regexes (e.g. unmatched `[` or `(`).

4. **Mostly single-segment filter strings**  
   Each setter call **appends** one or more filters (there is no clear). To avoid unbounded list growth over 1000 iterations, we generate a single segment about 70% of the time and 2–3 segments otherwise.

5. **Process dict coverage**  
   `gen_process_dict()` returns empty dict, minimal `name` or `cmdline`, both, or richer dicts with `username`/`user` for key:pattern filters. Values can be str, list of str, or None (implementation catches TypeError and returns False). This covers the branches in `_is_process_filtered` (key None vs key set, list vs string for cmdline).

6. **Logger and environment**  
   Importing `glances.filter` triggers the package root, which configures the Glances logger. The entry point sets `XDG_CACHE_HOME` to a directory under the project (`.cache`) **before** importing Glances, and ensures that directory exists.

---

## How to run

From the **project root**, with the SUT environment activated (see `state_testing/README.md`):

```bash
# Create/activate SUT venv if needed
python -m venv .venv-sut && source .venv-sut/bin/activate
pip install -e .

# Run the fuzzer (1000 iterations)
python -m state_testing.filter.filter_glances_entry
```

Or call `dummyTester()` from that module. Success criterion: the loop completes 1000 iterations without errors.

---

## Executors

- **Executor 1 – filter setter:** Generator `[gen_filter_string]`. Calls `setattr(sut, 'filter', s)`.
- **Executor 2 – filter getter:** No generators. Calls `sut.filter` (returns the list of filters).
- **Executor 3 – is_filtered:** Generator `[gen_process_dict]`. Calls `sut.is_filtered(process)`.

No executors are commented out; no API bugs were found during development.

---

## Pitfalls and reimplementation notes

- **Setter appends; no clear:** The filter setter splits on `,` and **appends** one `GlancesFilter` per segment. There is no public method to clear the list. Do not assume setting an empty string clears; empty string `""` is one segment that compiles and adds one filter.
- **Filter string must be a string:** The setter calls `value.split(',')`; passing `None` would raise. The generator always returns a string.
- **Compilable regexes only:** Generating invalid regex segments (e.g. `[`, `(?! )`) does not crash (the implementation catches and makes that filter inactive) but makes abstract state harder to reason about; the fuzzer uses only known-good patterns and safe fragments.
- **Import order:** Set `XDG_CACHE_HOME` (and create the directory) before any `from glances...` import, or the logger may try to write to a non-writable path and raise.
- **SUT environment:** Run with a venv that has `pip install -e .` so that `glances` is available; otherwise import fails.
- **No try/except:** Do not wrap executor calls in try/except to hide failures; fix preconditions in the generators or document API bugs and comment out the executor.
