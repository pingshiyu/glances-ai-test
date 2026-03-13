# GlancesPluginModel (view/history/alert only) – Initial semantics (fixed)

Component: `glances/plugins/plugin/model.py` – class `GlancesPluginModel`.

This document is fixed after Step 1 and must not be changed.

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

### Stats

#### `set_stats(input_stats)`
- **Preconditions:** None. `input_stats` can be a dict or list of dicts; typically keys/fields should match plugin expectations for `update_views()` and `get_export()` to behave sensibly.
- **Postconditions:** `self.stats = input_stats`. No other state change.
- **Higher-order:** No.

#### `get_raw()`
- **Preconditions:** None.
- **Postconditions:** Returns `self.stats`. No side effects.
- **Higher-order:** No.

#### `get_export()`
- **Preconditions:** None. By default returns `get_raw()`; subclasses may override.
- **Postconditions:** Returns the stats object to export (default: raw stats). No side effects.
- **Higher-order:** No.

#### `get_stats()` / `get_json()`
- **Preconditions:** None. `get_raw()` must be JSON-serialisable (dict/list of dicts with simple types).
- **Postconditions:** Returns JSON string of `get_raw()`. No side effects.
- **Higher-order:** No.

#### `reset()`
- **Preconditions:** None.
- **Postconditions:** `self.stats = self.get_init_value()`. No other state change.
- **Higher-order:** No.

#### `get_init_value()`
- **Preconditions:** None.
- **Postconditions:** Returns a copy of `stats_init_value`. No side effects.
- **Higher-order:** No.

---

### Views

#### `update_views()`
- **Preconditions:** `get_raw()` is not None. If stats is a list, `get_key()` must not be None and each item must have that key. Iteration over `listkeys(self.get_raw())` or over list items must not raise.
- **Postconditions:** `self.views` is rebuilt from current stats; each field gets a view dict (decoration, optional, additional, splittable, hidden). Returns `self.views`. May call `get_alert` / `get_alert_log` for decoration when `fields_description` has alert/log.
- **Higher-order:** No.

#### `get_views(item=None, key=None, option=None)`
- **Preconditions:** If `item` is not None, `item` must be a key in `self.views` (otherwise **KeyError**). If `key` is not in `item_views`, returns `'DEFAULT'` (no crash). If `option` not in `item_views[key]`, returns `'DEFAULT'`.
- **Postconditions:** Returns the views for the given item/key/option or the whole views dict. No side effects.
- **Higher-order:** No.

#### `get_json_views(item=None, key=None, option=None)`
- **Preconditions:** Same as `get_views`.
- **Postconditions:** Returns `json_dumps(get_views(...))`. No side effects.
- **Higher-order:** No.

#### `set_views(input_views)`
- **Preconditions:** None. `input_views` should be a dict (of dicts) for consistency with `get_views`.
- **Postconditions:** `self.views = input_views`. No other state change.
- **Higher-order:** No.

#### `reset_views()`
- **Preconditions:** None.
- **Postconditions:** `self.views = {}`. No other state change.
- **Higher-order:** No.

---

### History

#### `update_stats_history()`
- **Preconditions:** History must be enabled (`history_enable()` is True). `get_export()` must return a dict or list such that for each entry in `get_items_history_list()`, the item name exists in the export (for dict: key in export; for list: key in each list item). `_limits['history_size']` is used; default set in `load_limits` or init.
- **Postconditions:** For each history item, adds a point to `stats_history`. No return value.
- **Higher-order:** No.

#### `get_raw_history(item=None, nb=0)`
- **Preconditions:** `nb >= 0`. If `item` is not None, may return None if that item has no history (no crash).
- **Postconditions:** Returns stats history (dict of lists if item None, else list for that item, or None). No side effects.
- **Higher-order:** No.

#### `get_export_history(item=None)`
- **Preconditions:** Same as `get_raw_history`.
- **Postconditions:** Same as `get_raw_history(item=item)`. No side effects.
- **Higher-order:** No.

#### `get_stats_history(item=None, nb=0)`
- **Preconditions:** Same as `get_raw_history`. Internal uses `get_json` and `dictlist_json_dumps`.
- **Postconditions:** Returns history in JSON format. No side effects.
- **Higher-order:** No.

#### `get_trend(item, nb=30)`
- **Preconditions:** None. If `get_raw_history(item=item, nb=nb)` returns None or list with length < nb, returns None (no crash).
- **Postconditions:** Returns difference of means (second half minus first half of last nb values), or None. No side effects.
- **Higher-order:** No.

#### `reset_stats_history()`
- **Preconditions:** None. Only has effect when history is enabled.
- **Postconditions:** `stats_history.reset()`. No return value.
- **Higher-order:** No.

---

### Alert

#### `get_alert(current=0, minimum=0, maximum=100, highlight_zero=True, is_max=False, header=None, action_key=None, log=False)`
- **Preconditions:** `maximum` should not be 0 (implementation computes `(current * 100) / maximum` → **ZeroDivisionError** if maximum is 0). Other args can be any numeric/optional.
- **Postconditions:** Returns alert string (e.g. 'OK', 'CAREFUL', 'WARNING', 'CRITICAL', 'DEFAULT', 'MAX', or with '_LOG' suffix). May call `glances_thresholds.add(stat_name, trigger)` and `glances_events.add(...)` when log/trigger apply. Invalid trigger passed to `add` causes it to return False (no exception).
- **Higher-order:** No.

#### `get_alert_log(current=0, minimum=0, maximum=100, header="", action_key=None)`
- **Preconditions:** Same as `get_alert` (maximum != 0).
- **Postconditions:** Calls `get_alert(..., log=True)`. Same behaviour.
- **Higher-order:** No.

---

### Accessors

#### `get(item, default=None)`
- **Preconditions:** None. If `item` not in stats (dict or list-to-dict), returns `default`.
- **Postconditions:** Returns `self[item]` or default. No side effects.
- **Higher-order:** No.

#### `keys()`
- **Preconditions:** None. Stats may be dict or list (then `list_to_dict(stats).keys()`).
- **Postconditions:** Returns list of keys. No side effects.
- **Higher-order:** No.

#### `get_item_info(item, key, default=None)`
- **Preconditions:** None. If `fields_description` is None or `item` not in it, returns `default`.
- **Postconditions:** Returns `fields_description[item].get(key, default)`. No side effects.
- **Higher-order:** No.

---

### Limits / config

#### `get_limits(item=None)`
- **Preconditions:** None.
- **Postconditions:** If item is None, returns full `_limits` dict; else returns `_limits.get(plugin_name + '_' + item, None)`. No side effects.
- **Higher-order:** No.

#### `set_limits(item, value)`
- **Preconditions:** None. `value` can be numeric or list (e.g. for comma-separated config).
- **Postconditions:** `_limits[plugin_name + '_' + item] = value`. No return value.
- **Higher-order:** No.

#### `limits` (property getter / setter)
- **Preconditions:** None.
- **Postconditions:** Getter returns `_limits`; setter sets `_limits = input_limits`.
- **Higher-order:** No.

#### `get_refresh()` / `get_refresh_time()`
- **Preconditions:** None. If `get_limits('refresh')` is None, uses `args.time` if present else 2.
- **Postconditions:** Returns refresh time. No side effects.
- **Higher-order:** No.

#### `set_refresh(value)`
- **Preconditions:** None.
- **Postconditions:** Calls `set_limits('refresh', value)`. No return value.
- **Higher-order:** No.

#### `load_limits(config)`
- **Preconditions:** `config` must have `has_section`, `get_float_value`, `get_value`, `items` (or at least `has_section`; if not, returns False without modifying limits beyond default `history_size`).
- **Postconditions:** Sets `_limits['history_size']` and plugin-specific limits from config. Returns True if config was processed, else False.
- **Higher-order:** No.

---

### Other (dict-stats plugins only for some)

#### `sorted_stats()`
- **Preconditions:** If `get_key()` is None (dict stats), returns `self.stats` (no sort). If list stats, each item must have `get_key()` and value suitable for `re.split` and sort key (TypeError/KeyError possible for malformed data).
- **Postconditions:** Returns sorted list or stats. No side effects.
- **Higher-order:** No.

#### `filter_stats(stats)`
- **Preconditions:** `stats` is dict, list of dicts, or has `_asdict()`. Keys in stats that are not in `fields_description` are filtered out.
- **Postconditions:** Returns filtered copy. No side effects on self.
- **Higher-order:** No.

---

## Excluded (not in scope)

- **update()** – real I/O (psutil, etc.).
- **get_stats_snmp()** – network I/O.
- **msg_curse()**, **get_stats_display()**, **curse_add_line()**, etc. – display helpers (can be fuzzed with random args but may depend on curses/args).
- **manage_action()** – runs commands via `actions.run()`; would require mocking `secure_popen`.

---

## Higher-order functions

None in this API. No callbacks or function-valued arguments in the listed methods.
