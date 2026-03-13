# get_plugin_dependencies (dag.py) – Initial semantics (fixed)

Component: `glances/plugins/plugin/dag.py` – function `get_plugin_dependencies`.

This document is fixed after Step 1 and must not be changed.

---

## Abstract state

For a pure function, the "state" is the input abstraction: a **plugin name** (hashable, typically str) and an optional **dependency graph** (dict-like: keys = plugin names, values = iterables of dependency names). The function does not mutate the graph.

---

## Public API

### `get_plugin_dependencies(plugin_name, _graph=_plugins_graph)`

- **Preconditions:** `plugin_name` is hashable (used in `set`); `_graph` supports `.get(key, default)` and values are iterables of hashables (used in `_resolve(dep)` and `seen.add(plugin)`). No requirement that `plugin_name` be in the graph; cycles are handled via a `seen` set.
- **Postconditions:** Returns a list whose first element is `plugin_name`, followed by transitive dependencies (including from `_graph.get('*', [])`) in depth-first order, with no duplicate entries and with `plugin_name` excluded from the dependency tail.
- **Higher-order:** No.

---

## Higher-order functions

None in this API.
