# get_plugin_dependencies (dag) fuzzer: structure and design

This document describes the state-based fuzzer for **glances/plugins/plugin/dag.py** (`get_plugin_dependencies`), so another agent or a human can understand how it was implemented and reimplement or extend it without repeating common mistakes.

---

## Overview

The fuzzer drives the single public API of the DAG component—`get_plugin_dependencies(plugin_name, _graph=_plugins_graph)`—with random inputs over 1000 iterations. It uses the state_testing framework (`make_executor`, generators) and does **not** use try/except to absorb errors: preconditions are enforced by generators so that valid inputs are produced. There is **no SUT instance**; the API is a pure function.

---

## File roles

| File | Role |
|------|------|
| **dag_entry.py** | Entry point. Sets `XDG_CACHE_HOME` before any Glances import, builds the executor list via `get_executors()` (no SUT), and runs 1000 iterations: each iteration picks a random executor and runs it. Defines `dummyTester()`. |
| **dag_lib.py** | Defines `get_executors()`. Returns a list of callables; each callable is an executor that runs one or two generators and calls `get_plugin_dependencies` with the generated arguments. |
| **dag_generators.py** | No-arg generator callables: `gen_plugin_name()`, `gen_graph()`. They return values satisfying the API preconditions (hashable plugin name; dict with .get and iterable-of-hashable values). |
| **initial_semantics.md** | Fixed specification (never edit after Step 1): abstract state (input abstraction only), pre/postconditions for `get_plugin_dependencies`. |
| **working_semantics.md** | Copy of initial semantics; update only when refining after crashes or documenting bugs. |

---

## Design decisions

1. **No abstract state to maintain**  
   The API is a pure function; there is no SUT object to keep in sync. The "abstract state" in the semantics is only the input abstraction (plugin_name + optional graph). Executors do not update any shared state between runs.

2. **Two executors**  
   - **Executor A (default graph):** One generator `gen_plugin_name`. Calls `get_plugin_dependencies(name)` so the real `_plugins_graph` is used. Exercises realistic use and known plugin names.  
   - **Executor B (custom graph):** Two generators `gen_plugin_name`, `gen_graph`. Calls `get_plugin_dependencies(name, graph)`. Exercises arbitrary graphs (empty, cycles, deep chains, random) to broaden input coverage.

3. **Graph shape**  
   Generators produce `dict[str, list[str]]` so that `.get(key, default)` and iteration over dependency lists are always valid, and all values added to the internal `seen` set are hashable. We do not generate non-iterable values or non-hashable dependency names.

4. **Plugin name coverage**  
   `gen_plugin_name()` mixes: known names from the default graph (`*`, `cpu`, `load`, `alert`, etc.), random short alphanumeric names, and the empty string. This covers "in graph", "not in graph", and the special `*` key.

5. **Graph edge cases**  
   `gen_graph()` returns empty dict, `{'*': []}`, `{'*': ['x']}`, single node, chain, cycle (`a->b->a`), deep chain, and random small graphs. The implementation uses a `seen` set so cycles do not cause infinite loops; we include them to stress ordering and deduplication.

6. **Logger and environment**  
   The entry point sets `XDG_CACHE_HOME` to a directory under the project (`.cache`) **before** importing anything that pulls in Glances (the lib imports `glances.plugins.plugin.dag`). This avoids logger write issues.

---

## How to run

From the **project root**, with the SUT environment activated (see `state_testing/README.md`):

```bash
# Create/activate SUT venv if needed
python -m venv .venv-sut && source .venv-sut/bin/activate
pip install -e .

# Run the fuzzer (1000 iterations)
python -m state_testing.dag.dag_entry
```

Or run the pytest:

```bash
pytest state_testing/test_dag_fuzzer.py -v
```

Success criterion: the loop completes 1000 iterations without errors.

---

## Executors

- **Executor 1 – default graph:** Generators `[gen_plugin_name]`. Calls `get_plugin_dependencies(name)`.
- **Executor 2 – custom graph:** Generators `[gen_plugin_name, gen_graph]`. Calls `get_plugin_dependencies(name, graph)`.

No executors are commented out; no API bugs were found during development.

---

## Pitfalls and reimplementation notes

- **Pure function:** Do not introduce a fake SUT or shared mutable state. The function has no side effects and does not mutate the graph.
- **Hashable inputs:** `plugin_name` and every dependency name from the graph are added to a `set`; non-hashable values (e.g. lists) would raise. Generators use only strings (and the default graph uses strings).
- **Graph values must be iterables of hashables:** The code does `for dep in _graph.get(plugin, [])` and `seen.add(plugin)`. So each value must be iterable and yield hashables. We use `list[str]` only.
- **Import order:** Set `XDG_CACHE_HOME` (and create the directory) before importing the dag lib (which imports Glances).
- **SUT environment:** Run with a venv that has `pip install -e .` so that `glances` is available.
- **No try/except:** Do not wrap executor calls in try/except; fix preconditions in the generators or document API bugs and comment out the executor.
