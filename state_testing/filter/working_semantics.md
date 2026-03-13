# GlancesFilterList / GlancesFilter – Working semantics (updated during fuzzer development)

Component: `glances/filter.py` – classes `GlancesFilterList` and `GlancesFilter`.

This document is a copy of the initial semantics and may be updated when refining pre/postconditions after fuzzer crashes or findings.

---

## Abstract state

- **GlancesFilterList:** A list of filters. Each element is a `GlancesFilter`. The list only grows (setter appends); there is no public clear/reset. Each filter is either "active" (has a compiled regex and optionally a key) or "inactive" (regex compile failed for that segment; that filter's `_filter`/`_filter_re` are `None`; `is_filtered` for that filter always returns False).

- **GlancesFilter (single):** `_filter_input` (string or None), `_filter` (pattern string or None), `_filter_key` (str or None), `_filter_re` (compiled regex or None). Setter: `value` can be `None` (clears this filter); or `"pattern"` (key None, match on name/cmdline) or `"key:pattern"` (match on `process[key]`). On `re.compile` failure the filter is reset to inactive (no exception).

---

## Public API (GlancesFilterList – primary SUT)

### `filter` (setter)

- **Preconditions:** `value` must be a string (the implementation calls `value.split(',')`; passing non-string may raise).
- **Postconditions:** For each comma-separated segment, one `GlancesFilter` is created and appended to the list. Each segment is passed to a `GlancesFilter` setter: if the segment compiles as a regex (or is `key:pattern` with compilable pattern), that filter is active; otherwise that filter is inactive (implementation catches exception and sets that filter's state to None). No return value.
- **Higher-order:** No.

### `filter` (getter)

- **Preconditions:** None.
- **Postconditions:** Returns the internal list of `GlancesFilter` objects (read-only semantics for the caller).
- **Higher-order:** No.

### `is_filtered(process)`

- **Preconditions:** `process` is a dict. The implementation tolerates missing keys (KeyError → False for that filter), and None or non-string values (TypeError/AttributeError in `fullmatch` → False for that filter).
- **Postconditions:** Returns True iff at least one active filter matches the process. Matching: for each filter, if `filter_key` is None, match is on `process['name']` or `process['cmdline']` (fullmatch); if `filter_key` is set, match is on `process[filter_key]`. For `cmdline` as list with len>0, the implementation uses the first element; else it joins the list. KeyError/TypeError/AttributeError during match yield False for that filter.
- **Higher-order:** No.

---

## Edge cases (semantics)

- Empty string filter: `""` compiles as regex (matches empty string); one active filter is appended.
- `key:pattern` form: segment is split on first `:`; key is the part before, pattern the part after; pattern must compile.
- Regex that fails to compile: that filter becomes inactive; no exception propagates.
- Process with missing `name`/`cmdline`/key: that filter returns False (KeyError).
- `process[key]` None or non-string: implementation may raise TypeError in `fullmatch`; caught and returns False.
- `cmdline` as list vs string: both handled; list with >0 elements uses first element for matching.

---

## Higher-order functions

None in this API.
