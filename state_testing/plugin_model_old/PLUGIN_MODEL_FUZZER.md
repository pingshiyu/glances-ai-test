# GlancesPluginModel state-based fuzzer

This document describes the structure, design decisions, and implementation of the state-based fuzzer for **component 7**: `GlancesPluginModel` (view/history/alert API only), as in `prompts/state-based-testing-overview.md`.

## Purpose

Drive the public API of `GlancesPluginModel` (and MemPlugin as the concrete instance) with random sequences of calls, without calling `update()` (real I/O) or `get_stats_snmp()` (network). The fuzzer helps infer and document pre/postconditions and find bugs.

## File layout

```
state_testing/plugin_model/
├── initial_semantics.md           # Fixed semantics (never change)
├── working_semantics.md            # Copy; updated when refining after crashes
├── plugin_model_glances_entry.py   # Entry point: dummyTester(), 1000 iterations
├── plugin_model_glances_generators.py  # Random generators (precondition-safe)
├── plugin_model_glances_lib.py     # Executors: (guard, executor) pairs
├── __init__.py
└── PLUGIN_MODEL_FUZZER.md          # This file
```

Top-level: `state_testing/test_plugin_model_fuzzer.py` – pytest that runs `dummyTester()`.

## Design decisions

### Plugin choice

- **MemPlugin** is used as the SUT. It has dict-shaped `stats`, a simple `fields_description`, and `items_history_list` with one item (`percent`). History is **disabled** by default in the fuzzer (`args.disable_history=True`) to reduce precondition surface (no need to maintain history item names in `set_stats` for `update_stats_history`).

### Abstract state and guards

- **Stats:** Must always include `'percent'`, `'used'`, `'total'` when we allow **update_views** to run, because MemPlugin’s `update_views()` override does `self.views['percent']['decoration'] = self.get_alert_log(self.stats['used'], maximum=self.stats['total'])`. The fuzzer therefore:
  - Uses **guarded executors**: `get_executors(plugin)` returns `(guard, executor)` pairs. For `update_views`, the guard is `_can_update_views(plugin)` (stats is dict and contains `percent`, `used`, `total`). Each iteration only picks from executors whose guard is `None` or returns True.
  - Ensures **gen_stats_dict()** always includes `percent`, `used`, `total` so that after `set_stats`, the guard can become True.

### Generators

- **get_views(item, key, option):** If `item` is not None, `item` must be in `self.views` (else KeyError). **gen_views_args(plugin)** returns a no-arg callable that, when called, reads `plugin.views` and returns either `(None, None, None)` or a valid `(item, key, option)` from the current views. So we never pass an invalid `item`.
- **get_alert / get_alert_log:** Implementation does `(current * 100) / maximum`; **maximum must not be 0**. **gen_get_alert_maximum()** returns a positive int/float. Also, **gen_limits_value()** returns only numeric values (no list), because `set_limits` can store values that `get_limit()` returns to `get_alert`, which then compares with `>=`; a list would cause TypeError.
- **gen_trend_item(plugin)** must **return** the inner callable (factory was missing `return f`, causing TypeError in the executor).
- **load_limits(config):** Config must have `has_section` (and ideally `get_float_value`, `get_value`, `items`). **gen_config()** returns a minimal SimpleNamespace that implements these so `load_limits` does not crash.

### Excluded methods

- **update()** – real I/O (psutil, etc.).
- **get_stats_snmp()** – network.
- **msg_curse**, **get_stats_display**, **curse_add_*** – display helpers (not in scope).
- **manage_action** – runs commands; would require mocking `secure_popen`.

### Limits setter

- The executor for the `limits` property setter does `setattr(plugin, 'limits', dict(getattr(plugin, '_limits', {})))` so we only reset `_limits` to a copy of itself, avoiding injection of arbitrary keys that could break internal assumptions.

## How to run

From project root with SUT environment (see `state_testing/README.md`):

```bash
source .venv-sut/bin/activate
pip install -e .
python -m state_testing.plugin_model.plugin_model_glances_entry
```

Or via pytest:

```bash
pytest state_testing/test_plugin_model_fuzzer.py -v
```

Success: 1000 iterations complete without errors.

## Crashes and fixes

See **working_semantics.md** section “Crashes”. All issues so far were **fuzzer bugs** (missing return, missing guard, generator producing invalid limit type); no API bugs were left in the executors.

## Reimplementation notes

- When adding a new executor that depends on plugin state, either make the generator **stateful** (factory taking `plugin` and returning a no-arg callable that reads current state) or add a **guard** and filter in the entry loop.
- For any plugin that overrides `update_views()` and assumes specific keys in `stats`, ensure generated stats always include those keys and/or guard the `update_views` executor.
- Keep **gen_limits_value** numeric if that value can later be used in comparisons (e.g. `get_alert`).
