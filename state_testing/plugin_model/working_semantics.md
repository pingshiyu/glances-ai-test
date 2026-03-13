# GlancesPluginModel – Working semantics

Component: `glances/plugins/plugin/model.py` – class `GlancesPluginModel`.

This document is a copy of the initial semantics and may be updated when refining pre/postconditions or documenting crashes.

---

## Abstract state

- **stats:** Dict or list of dicts; the current plugin data. Set by `set_stats`, reset by `reset`. Read by `get_raw`, `get_export`, `update_views`, `update_stats_history`, `get_stats_action`.
- **views:** Dict built by `update_views`; maps field/key to view info (decoration, optional, etc.). Initially `{}`; updated when `update_views()` is called after `stats` is set.
- **stats_history:** A `GlancesHistory` instance; updated by `update_stats_history()` when history is enabled and `_limits['history_size']` exists. Keys come from history items; values are time-series.
- **_limits:** Dict. Keys include `history_size` (int) and `{plugin_name}_{item}` for item in `careful`, `warning`, `critical`, `refresh`, `log`, etc. Values: float for thresholds/refresh; list for `log` (e.g. `['True']`). Used by `get_alert`, `get_limit`, `get_limit_log`, `get_limit_action`, `update_stats_history`.
- **actions:** `GlancesActions` instance; `manage_threshold` and `manage_action` call into it (`add` on global thresholds, `set`/`run` on actions). External to the plugin’s abstract state but side-effecting.

---

## Public API (fuzzer-relevant)

### `set_stats(input_stats)`

- **Preconditions:** None. `input_stats` is typically a dict (for dict-based plugins like mem) or list of dicts (for list-based plugins).
- **Postconditions:** `stats` is set to `input_stats`. No other state change.
- **Higher-order:** No.

### `update_views()`

- **Preconditions:** None. If `get_raw()` is `None` or not dict/list as expected, `views` may stay or become `{}`.
- **Postconditions:** `views` is rebuilt from current `stats` via `_build_view_for_field` for each field/key. Returns `self.views`.
- **Higher-order:** No.

### `update_stats_history()`

- **Preconditions:** `history_enable()` is true; `_limits['history_size']` exists (otherwise KeyError). For dict stats, each `i['name']` from `get_items_history_list()` must be a key in `get_export()` (else KeyError). The fuzzer enforces this by having `gen_mem_stats()` always include keys for all history item names (e.g. `percent` for mem).
- **Postconditions:** For each history item, one entry is added to `stats_history` with `history_max_size=self._limits['history_size']`. No change if history disabled or export empty.
- **Higher-order:** No.

### `get_views(item=None, key=None, option=None)`

- **Preconditions:** If `item` is not `None`, then `item` must be a key in `views` (else KeyError). If `key` is not `None`, it should be in `item_views`; if `option` is not `None`, it should be in `item_views[key]` for correct semantics (otherwise returns `'DEFAULT'`).
- **Postconditions:** Returns the view for the given (item, key, option), or `'DEFAULT'` when key/option not found. No state change.
- **Higher-order:** No.

### `get_raw()`

- **Preconditions:** None.
- **Postconditions:** Returns `stats`. No state change.
- **Higher-order:** No.

### `get_export()`

- **Preconditions:** None.
- **Postconditions:** By default returns `get_raw()`. No state change.
- **Higher-order:** No.

### `get_alert(current=0, minimum=0, maximum=100, highlight_zero=True, is_max=False, header=None, action_key=None, log=False)`

- **Preconditions:** None. If `maximum == 0`, implementation catches ZeroDivisionError and returns `'DEFAULT'`. `current`/`minimum`/`maximum` can be numeric; non-numeric may yield TypeError and return `'DEFAULT'`.
- **Postconditions:** Computes percentage from current/maximum; compares to `_limits` (careful/warning/critical); may call `glances_events.add`, `manage_threshold`, `manage_action`. Returns one of `'DEFAULT'`, `'OK'`, `'CAREFUL'`, `'WARNING'`, `'CRITICAL'`, optionally with `_LOG` suffix. State change: global thresholds and actions may be updated.
- **Higher-order:** No (but side effects: events, thresholds, actions).

### `get_alert_log(current=0, minimum=0, maximum=100, header="", action_key=None)`

- **Preconditions:** Same as `get_alert` for numeric/string args.
- **Postconditions:** Calls `get_alert(..., log=True)`. Same return and side effects.
- **Higher-order:** No.

### `set_limits(item, value)`

- **Preconditions:** None. `item` is a string (e.g. `'careful'`, `'warning'`, `'critical'`, `'refresh'`, `'log'`). For `'log'`, `value` is typically a list (e.g. `['True']`) for `get_limit_log` to interpret.
- **Postconditions:** `_limits[f'{plugin_name}_{item}'] = value`. No other state change.
- **Higher-order:** No.

### `load_limits(config)`

- **Preconditions:** `config` must have `has_section` attribute (else returns False after setting `_limits['history_size'] = 28800`). If `config.has_section(section)` is used, `config` should provide `get_float_value(section, option, default)` and `get_value(section, option).split(",")` where needed.
- **Postconditions:** Sets `_limits['history_size']` to 28800 or from config. If plugin section exists, populates `_limits` from config. Returns True.
- **Higher-order:** No.

### `manage_threshold(stat_name, trigger)`

- **Preconditions:** `trigger` is typically one of `'ok'`, `'careful'`, `'warning'`, `'critical'` (lowercase). Implementation calls `glances_thresholds.add(stat_name, trigger)` (global).
- **Postconditions:** Global thresholds object is updated. No change to plugin’s _limits.
- **Higher-order:** No.

### `manage_action(stat_name, trigger, header, action_key)`

- **Preconditions:** None. If `get_limit_action` returns a command, `actions.run` is called (requires secure_popen or similar to be safe in tests).
- **Postconditions:** Either `actions.set(stat_name, trigger)` or `actions.run(...)` with mustache-rendered command. No change to plugin’s _limits.
- **Higher-order:** No.

### `reset()`

- **Preconditions:** None.
- **Postconditions:** `stats` is set to `get_init_value()` (copy of stats_init_value). No other state change.
- **Higher-order:** No.

### `get_limits(item=None)`

- **Preconditions:** None.
- **Postconditions:** If `item is None`, returns full `_limits` dict. Otherwise returns `_limits.get(f'{plugin_name}_{item}', None)`. No state change.
- **Higher-order:** No.

---

## Higher-order functions

None in this API (no callbacks passed in by the caller; actions.run executes commands but does not take a function from the plugin).
