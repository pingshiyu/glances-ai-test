# GlancesPluginModel (view/history/alert only) – Working semantics

Component: `glances/plugins/plugin/model.py` – class `GlancesPluginModel`.

This document is a copy of the initial semantics; update it when refining pre/postconditions after fuzzer crashes.

Scope: drive view, history, and alert API only. Do **not** call `update()` (real I/O) or `get_stats_snmp()` (network).

---

## Abstract state

- **stats:** The current stats object: either a dict (e.g. mem plugin) or a list of dicts (e.g. network, fs). Set by `set_stats()` or `reset()`; read by `get_raw()`, `get_export()`, etc.
- **views:** A dict built by `update_views()`. For dict stats: keys are field names (from `listkeys(stats)`). For list stats: keys are `i[get_key()]` for each item `i` in stats; each value is a dict of field names to view options (decoration, optional, etc.). If `update_views()` has not been called after the current `stats`, views may be stale or empty.
- **stats_history:** A `GlancesHistory` instance. Populated by `update_stats_history()` only when **history is enabled**: `args is not None`, `not args.disable_history`, and `get_items_history_list()` is not None. When history is disabled, `update_stats_history()` returns without doing work; `get_raw_history` returns empty or from previous state.
- **_limits:** Dict of limit/config keys (e.g. `history_size`, `mem_refresh`). Set by `load_limits(config)` or `set_limits(item, value)`; read by `get_limits(item)`.
- **fields_description:** Dict of field metadata (description, unit, optional, rate, alert, log, mmm). Set at init; read by `get_item_info`, `_build_field_decoration`, etc.
- **get_key():** For list-of-dict stats, the key used to index items (e.g. interface name). For dict stats (e.g. mem), returns `None`.

---

## Public API (in scope)

(Same as initial_semantics.md; see that file for full pre/postconditions. Summary: stats, views, history, alert, accessors, limits, sorted_stats, filter_stats.)

---

## Crashes (record here when found)

### Fuzzer bugs (fixed)

1. **gen_trend_item(plugin) returned None** – The factory did not `return f`, so the executor received a non-callable. Fixed by adding `return f` in `plugin_model_glances_generators.py`.

2. **MemPlugin.update_views() KeyError: 'percent'** – MemPlugin’s override assumes `stats` contains `'percent'`, `'used'`, `'total'` and assigns `self.views['percent']['decoration'] = ...`. If stats was empty or lacked those keys (e.g. after `reset()` or a minimal `set_stats`), views did not contain `'percent'`. Fixed by: (a) making `gen_stats_dict()` always include `'percent'`, `'used'`, `'total'`; (b) adding a guard `_can_update_views(plugin)` so the `update_views` executor only runs when stats has those keys.

3. **get_alert TypeError: '>=' not supported between 'float' and 'list'** – `set_limits(item, value)` was sometimes called with `value` a list (from `gen_limits_value()`). Later `get_alert` used `get_limit('critical', ...)` which can return that list, and compared `value >= critical`. Fixed by making `gen_limits_value()` return only int/float.

### API bugs

None so far.
