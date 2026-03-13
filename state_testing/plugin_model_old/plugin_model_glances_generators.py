#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Random generators for GlancesPluginModel (view/history/alert) fuzzer.
# Each generator is a no-arg callable (or factory returning one) that returns
# values satisfying preconditions for the API.
#

import random
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

# Mem plugin fields (dict stats)
MEM_FIELDS = (
    'total', 'available', 'percent', 'used', 'free',
    'active', 'inactive', 'buffers', 'cached', 'wired', 'shared',
)


def gen_stats_dict() -> dict[str, Any]:
    """Stats dict for set_stats(): subset of mem-like keys with int/float values.
    Always includes 'percent', 'used', 'total' so MemPlugin.update_views() override does not KeyError.
    Covers empty (only required keys), minimal, and full dicts.
    """
    required = ('percent', 'used', 'total')  # MemPlugin.update_views() expects these
    choice = random.choice(['minimal', 'medium', 'full'])
    if choice == 'minimal':
        keys = list(required) + random.sample([k for k in MEM_FIELDS if k not in required], min(1, len(MEM_FIELDS) - 3))
    elif choice == 'medium':
        keys = list(required) + random.sample([k for k in MEM_FIELDS if k not in required], min(4, len(MEM_FIELDS) - 3))
    else:
        keys = list(MEM_FIELDS)
    out = {}
    for k in keys:
        if k == 'percent':
            out[k] = round(random.uniform(0.0, 100.0), 1)
        else:
            out[k] = random.randint(0, 2**30) if random.random() < 0.7 else random.uniform(0, 1e9)
    if random.random() < 0.2:
        out['time_since_update'] = random.randint(0, 10)
    return out


def gen_views_args(plugin: Any) -> Callable[[], tuple[Any, Any, Any]]:
    """Factory: returns a no-arg callable that yields (item, key, option) valid for get_views.
    If views is empty, always returns (None, None, None). Otherwise sometimes None for item/key/option,
    or a key from views (and from views[item], views[item][key]).
    """
    def f() -> tuple[Any, Any, Any]:
        v = getattr(plugin, 'views', None) or {}
        if not v:
            return (None, None, None)
        # Often return no item (all views)
        if random.random() < 0.4:
            return (None, None, None)
        item = random.choice(list(v.keys()))
        item_views = v[item]
        if not item_views or random.random() < 0.3:
            return (item, None, None)
        key = random.choice(list(item_views.keys()))
        opts = item_views[key]
        if not isinstance(opts, dict) or random.random() < 0.3:
            return (item, key, None)
        option = random.choice(list(opts.keys()))
        return (item, key, option)
    return f


def gen_nb() -> int:
    """Non-negative int for history/get_raw_history(nb=...)."""
    if random.random() < 0.3:
        return 0
    return random.randint(0, 500)


def gen_trend_nb() -> int:
    """Positive int for get_trend(item, nb). Use small nb to avoid strict length requirement."""
    return random.randint(2, 30)


def gen_item_for_get(plugin: Any) -> Callable[[], str]:
    """Factory: returns a no-arg callable that yields a key that may exist in stats, or random string."""
    def f() -> str:
        raw = getattr(plugin, 'stats', None)
        if raw is None:
            return random.choice(list(MEM_FIELDS) + ['nonexistent'])
        if isinstance(raw, dict):
            keys = list(raw.keys())
        else:
            keys = []
        if keys and random.random() < 0.7:
            return random.choice(keys)
        return random.choice(list(MEM_FIELDS) + ['x', 'y', ''])
    return f


def gen_get_alert_maximum() -> int | float:
    """maximum for get_alert: must not be 0 (ZeroDivisionError)."""
    if random.random() < 0.5:
        return 100
    return random.randint(1, 1000) or 1


def gen_get_alert_current() -> int | float:
    return random.randint(0, 200)


def gen_get_alert_minimum() -> int | float:
    return random.randint(0, 50)


def gen_limits_item() -> str:
    """Item name for set_limits / get_limits."""
    return random.choice(['refresh', 'history_size', 'careful', 'warning', 'critical', 'limit'])


def gen_limits_value() -> int | float:
    """Value for set_limits: numeric only. Lists would break get_alert (>= compare)."""
    return random.randint(0, 10000)


def gen_item_info_item(plugin: Any) -> Callable[[], str]:
    """Factory: item for get_item_info; from fields_description or random."""
    def f() -> str:
        fd = getattr(plugin, 'fields_description', None) or {}
        if fd and random.random() < 0.7:
            return random.choice(list(fd.keys()))
        return random.choice(list(MEM_FIELDS) + ['unknown'])
    return f


def gen_item_info_key() -> str:
    """Key for get_item_info (e.g. description, unit, optional)."""
    return random.choice(['description', 'unit', 'short_name', 'optional', 'rate', 'alert', 'log', 'mmm', 'min_symbol'])


def gen_trend_item(plugin: Any) -> Callable[[], str]:
    """Factory: item for get_trend; when history disabled, any string is safe (returns None)."""
    def f() -> str:
        # Mem plugin history item is 'percent'
        return random.choice(['percent', 'used', 'total', ''])
    return f


def gen_raw_history_item(plugin: Any) -> Callable[[], str | None]:
    """Factory: item for get_raw_history(item=...). None or known history item."""
    def f() -> str | None:
        if random.random() < 0.5:
            return None
        return random.choice(['percent', 'used', 'total', ''])  # mem: percent is the history item
    return f


def _minimal_config() -> Any:
    """Minimal config object for load_limits: has_section returns False so no KeyError."""
    c = SimpleNamespace()
    c.has_section = lambda s: False
    c.get_float_value = lambda s, k, default=None: default
    c.get_value = lambda s, k: ''
    c.items = lambda s: []
    return c


def gen_config() -> Any:
    """Config for load_limits: minimal object that will not crash (has_section present)."""
    return _minimal_config()


def gen_views_dict() -> dict:
    """Input for set_views: empty or simple dict of dicts."""
    if random.random() < 0.5:
        return {}
    # Minimal view structure: one key with one field and options
    return {
        'k1': {
            'f1': {'decoration': 'DEFAULT', 'optional': False, 'hidden': False},
        }
    }


def gen_filter_stats_input(plugin: Any) -> Callable[[], dict | list]:
    """Input for filter_stats(stats): dict or list of dicts with keys that may overlap fields_description."""
    def f() -> dict | list:
        if random.random() < 0.5:
            return gen_stats_dict()
        return [gen_stats_dict() for _ in range(random.randint(1, 3))]
    return f
