# GlancesPluginModel fuzzer: structure and design

This document describes the state-based fuzzer for **glances/plugins/plugin/model.py** (GlancesPluginModel, view/history/alert only), so another agent or a human can understand how it was implemented and reimplement or extend it without repeating common mistakes.

---

## Overview

The fuzzer drives the public API of `GlancesPluginModel` (using one **MemPlugin** instance) with random inputs over **5000 iterations**. It uses the state_testing framework (`make_executor`, generators) and does **not** use try/except to absorb errors: preconditions are enforced by generators so that valid inputs are produced. **Full logic coverage** includes the alert path: `get_alert`, `get_alert_log`, `set_limits`, `manage_threshold`, `manage_action` are exercised with random parameters. The plugin’s `update()` is **not** called (no real I/O). Mocks are applied so `glances_events.add` and `secure_popen` are no-ops.

---

## File roles

| File | Role |
|------|------|
| **plugin_model_glances_entry.py** | Entry point. Sets `XDG_CACHE_HOME`, patches `glances.events_list.glances_events` and `glances.secure.secure_popen` **before** any Glances import, creates one MemPlugin with minimal args and `config=None`, sets `_limits['history_size']`, builds the executor list, and runs **5000** iterations: each iteration picks a random executor and runs it. Defines `dummyTester()`. |
| **plugin_model_glances_lib.py** | Defines `get_executors(sut)`. Returns a list of callables; each callable is an executor that runs one or more generators and calls one API method on `sut` with the generated arguments. |
| **plugin_model_glances_generators.py** | No-arg generator callables (and factories like `gen_views_args(sut)`) that return values satisfying the API preconditions. Used by the lib to build executors. |
| **initial_semantics.md** | Fixed specification (never edit after Step 1): abstract state, pre/postconditions for the fuzzer-relevant API. |
| **working_semantics.md** | Copy of initial semantics; update only when refining after crashes or findings. |

---

## Design decisions

1. **Single SUT instance (MemPlugin)**  
   One MemPlugin is shared by all executors so that random sequences of `set_stats`, `update_views`, `update_stats_history`, `get_views`, `get_alert`, `set_limits`, etc., exercise stateful behaviour.

2. **Mocks before import**  
   `glances_events` is patched so `add()` is a no-op (avoids global events list and dependencies on processes/thresholds inside `add`). `glances.secure.secure_popen` is patched so `manage_action` → `actions.run` never executes real commands. Both patches are started **before** importing MemPlugin.

3. **history_size and history items**  
   After constructing the plugin, the entry sets `sut._limits.setdefault('history_size', 28800)` so `update_stats_history()` does not KeyError. The generator `gen_mem_stats()` **always** includes every key required by the plugin’s history items (e.g. `percent` for mem), so `update_stats_history()` never sees a missing key in `get_export()`.

4. **State-dependent get_views**  
   `get_views(item, key, option)` raises KeyError if `item` is not in `self.views`. The executor uses a state-dependent generator `gen_views_args(sut)()` that returns `(None, None, None)` when `views` is empty, and otherwise picks `item` from `sut.views`, then `key` from `sut.views[item]`, and optionally `option` from nested dicts. This avoids KeyError without filtering executors in the entry.

5. **Full alert coverage**  
   Executors for `get_alert`, `get_alert_log`, `set_limits`, `load_limits`, `manage_threshold`, `manage_action` use generators that cover numeric edge cases (0, negative, large), booleans (`highlight_zero`, `is_max`, `log`), and optional strings (`header`, `action_key`). `set_limits` uses `gen_set_limits_pair()` so `value` is correct for `item` (e.g. list for `'log'`). Trigger values for `manage_threshold` / `manage_action` are lowercase (`'ok'`, `'careful'`, `'warning'`, `'critical'`).

6. **Mock config for load_limits**  
   `gen_mock_config()` returns an object with `has_section`, `items(section)`, `get_float_value`, `get_value`. For plugin-level options that are lists (e.g. `log`), `get_float_value` raises ValueError so the code uses `get_value(...).split(",")`; the mock returns comma-separated strings for those.

7. **No try/except**  
   Failures are not caught; preconditions are enforced in generators (and in one case by always including history keys in `gen_mem_stats`).

---

## How to run

From the **project root**, with the SUT environment activated (see `state_testing/README.md`):

```bash
# Create/activate SUT venv if needed
python -m venv .venv-sut && source .venv-sut/bin/activate
pip install -e .

# Run the fuzzer (5000 iterations)
python -m state_testing.plugin_model.plugin_model_glances_entry
```

Or call `dummyTester()` from that module. Success criterion: the loop completes 5000 iterations without errors.

---

## Executors

| # | API | Generators | Notes |
|---|-----|------------|--------|
| 1 | `set_stats(stats)` | `gen_mem_stats` | Stats always include history item keys (e.g. `percent`). |
| 2 | `update_views()` | — | |
| 3 | `update_stats_history()` | — | Safe because `history_size` is set and stats include history keys. |
| 4 | `get_views(item, key, option)` | `gen_views_args(sut)()` | State-dependent: (None, None, None) or valid (item, key, option). |
| 5 | `get_raw()` | — | |
| 6 | `get_export()` | — | |
| 7 | `get_alert(...)` | current, min, max, highlight_zero, is_max, header, action_key, log | Full logic coverage. |
| 8 | `get_alert_log(...)` | current, min, max, header, action_key | |
| 9 | `set_limits(item, value)` | `gen_set_limits_pair` | Pair (item, value) with value type correct for item. |
| 10 | `load_limits(config)` | `gen_mock_config` | Mock config with sections and get_float_value/get_value. |
| 11 | `manage_threshold(stat_name, trigger)` | `gen_stat_name`, `gen_trigger` | Trigger in ['ok','careful','warning','critical']. |
| 12 | `manage_action(stat_name, trigger, header, action_key)` | `gen_stat_name`, `gen_trigger`, `gen_header`, `gen_action_key` | |
| 13 | `reset()` | — | |
| 14 | `get_limits(item=None)` | `gen_limits_item_or_none` | |

No executors are commented out; no API bugs were found during development.

---

## Pitfalls and reimplementation notes

- **Import order:** Set `XDG_CACHE_HOME` (and create the directory) and **start the mocks** before any `from glances...` import. Otherwise the real `glances_events` and `secure_popen` are already bound.
- **update_stats_history:** Requires `_limits['history_size']` and that `get_export()` contains every `i['name']` from `get_items_history_list()`. The entry sets `history_size`; the generator ensures stats always include those names (e.g. `percent` for mem).
- **get_views(item, key, option):** If `item` is not None, it must be a key in `self.views`. Use a state-dependent generator that reads `sut.views` and returns only valid (item, key, option).
- **manage_threshold / manage_action:** The implementation passes trigger to `glances_thresholds.add(stat_name, trigger)` and to `actions.set`/`run`; use lowercase trigger values to match `get_alert` (which uses `ret.lower()`).
- **load_limits mock:** For plugin section options that are lists (e.g. `log`), the code does `get_float_value(...)` then on ValueError uses `get_value(...).split(",")`. The mock must raise ValueError for such options and return a comma-separated string from `get_value`.
- **SUT environment:** Run with a venv that has `pip install -e .` so that `glances` and its dependencies (e.g. `psutil`) are available.
