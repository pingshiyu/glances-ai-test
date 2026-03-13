#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Random generators for GlancesPluginModel (mem plugin) fuzzer. Each generator
# is a no-arg callable (or a factory returning one) that returns values
# satisfying preconditions for the API. Full logic coverage including alert path.
#

import random
from collections.abc import Callable
from typing import Any

# Mem plugin fields (subset for set_stats; ensures update_views/get_export work)
MEM_STAT_KEYS = (
    'total', 'available', 'percent', 'used', 'free',
    'active', 'inactive', 'buffers', 'cached', 'wired', 'shared',
)
LIMITS_ITEMS = ('careful', 'warning', 'critical', 'refresh', 'log')
TRIGGERS = ('ok', 'careful', 'warning', 'critical')
VIEW_OPTIONS = ('decoration', 'optional', 'additional', 'splittable', 'hidden')


# Mem plugin history items (update_stats_history requires these keys in get_export()).
MEM_HISTORY_NAMES = ('percent',)


def gen_mem_stats() -> dict:
    """Stats dict for set_stats(); keys from mem fields_description, numeric values.
    Always includes MEM_HISTORY_NAMES so update_stats_history() never KeyErrors.
    """
    n = random.randint(1, len(MEM_STAT_KEYS))
    keys = list(random.sample(list(MEM_STAT_KEYS), n))
    for k in MEM_HISTORY_NAMES:
        if k not in keys:
            keys.append(k)
    out = {}
    for k in keys:
        if k == 'percent':
            out[k] = random.choice([
                random.uniform(0.0, 100.0),
                random.randint(0, 100),
                0, 100,
            ])
        else:
            out[k] = random.choice([
                random.randint(0, 10**12),
                random.uniform(0, 1e12),
                0,
            ])
    return out


def gen_current() -> int | float:
    """Value for get_alert current."""
    return random.choice([
        random.randint(-100, 1000),
        random.uniform(-100.0, 1000.0),
        0, 100,
    ])


def gen_minimum() -> int | float:
    """Value for get_alert minimum."""
    return random.choice([
        random.randint(-50, 50),
        random.uniform(-50.0, 50.0),
        0,
    ])


def gen_maximum() -> int | float:
    """Value for get_alert maximum (0 yields DEFAULT)."""
    return random.choice([
        random.randint(0, 500),
        random.uniform(0.0, 500.0),
        0, 1, 100,
    ])


def gen_highlight_zero() -> bool:
    return random.choice([True, False])


def gen_is_max() -> bool:
    return random.choice([True, False])


def gen_header() -> str | None:
    if random.random() < 0.5:
        return None
    return random.choice(['', 'percent', 'used', 'total', 'x', 'h'])


def gen_action_key() -> str | None:
    if random.random() < 0.5:
        return None
    return random.choice(['', 'percent', 'key', 'a'])


def gen_log() -> bool:
    return random.choice([True, False])


def gen_limits_item() -> str:
    """Item for set_limits (careful, warning, critical, refresh, log)."""
    return random.choice(LIMITS_ITEMS)


def gen_limits_value(item: str):
    """Value for set_limits; for 'log' use list ['True']/['False']."""
    if item == 'log':
        return random.choice([['True'], ['False']])
    return random.choice([
        random.uniform(0, 100),
        random.randint(0, 100),
        0, 50, 80, 95,
    ])


def gen_limits_item_or_none() -> str | None:
    """For get_limits(item=None): None or an item string."""
    if random.random() < 0.3:
        return None
    return gen_limits_item()


def gen_stat_name() -> str:
    """Stat name for manage_threshold / manage_action."""
    return random.choice([
        'mem', 'percent', 'cpu', 'load', 'x', '',
        ''.join(random.choices('abcdefgh', k=random.randint(0, 8))),
    ])


def gen_trigger() -> str:
    """Trigger for manage_threshold / manage_action (lowercase)."""
    return random.choice(TRIGGERS)


class _MockConfig:
    """Mock config for load_limits: has_section, items, get_float_value, get_value."""

    def __init__(self, has_global: bool = True, has_plugin_section: bool = True):
        self._has_global = has_global
        self._has_plugin = has_plugin_section
        self._global = {'history_size': random.uniform(1000, 50000)}
        self._plugin = {}
        if has_plugin_section:
            for level in random.sample(LIMITS_ITEMS, random.randint(0, len(LIMITS_ITEMS))):
                if level == 'log':
                    self._plugin[level] = ['True'] if random.random() < 0.5 else ['False']
                else:
                    self._plugin[level] = random.uniform(0, 100)

    def has_section(self, section: str) -> bool:
        if section == 'global':
            return self._has_global
        return self._has_plugin

    def items(self, section: str):
        if section == 'global':
            return list(self._global.items())
        return list(self._plugin.items())

    def get_float_value(self, section: str, option: str, default=None):
        if section == 'global':
            return self._global.get(option, default if default is not None else 28800)
        v = self._plugin.get(option)
        if v is None:
            return default
        if isinstance(v, list):
            raise ValueError('list not float')
        return float(v)

    def get_value(self, section: str, option: str):
        v = self._plugin.get(option) if section != 'global' else self._global.get(option)
        if v is None:
            return ''
        if isinstance(v, list):
            return ','.join(str(x) for x in v)
        return str(v)


def gen_mock_config() -> _MockConfig:
    """Mock config for load_limits."""
    return _MockConfig(
        has_global=random.random() < 0.9,
        has_plugin_section=random.random() < 0.7,
    )


def gen_views_args(sut: Any) -> Callable[[], tuple[Any, Any, Any]]:
    """Factory: returns a no-arg callable that yields (item, key, option) valid for get_views.
    If views is empty, returns (None, None, None). Otherwise item in views, key in views[item] or None.
    """
    def f() -> tuple[Any, Any, Any]:
        if not getattr(sut, 'views', None) or len(sut.views) == 0:
            return (None, None, None)
        item = random.choice(list(sut.views.keys()))
        item_views = sut.views[item]
        if not item_views or random.random() < 0.3:
            return (item, None, None)
        key = random.choice(list(item_views.keys()))
        val = item_views[key]
        if isinstance(val, dict) and val and random.random() < 0.5:
            option = random.choice(list(val.keys()))
            return (item, key, option)
        return (item, key, None)
    return f


def gen_set_limits_pair() -> tuple[str, Any]:
    """Single (item, value) for set_limits; value depends on item."""
    item = gen_limits_item()
    return (item, gen_limits_value(item))
