#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executors for GlancesPluginModel (view/history/alert only): each executor
# runs generators and calls one API method on the shared plugin instance.
#

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TYPE_CHECKING

from state_testing.executor import make_executor

from .plugin_model_glances_generators import (
    gen_config,
    gen_filter_stats_input,
    gen_get_alert_current,
    gen_get_alert_maximum,
    gen_get_alert_minimum,
    gen_item_for_get,
    gen_item_info_item,
    gen_item_info_key,
    gen_limits_item,
    gen_limits_value,
    gen_nb,
    gen_raw_history_item,
    gen_stats_dict,
    gen_trend_item,
    gen_trend_nb,
    gen_views_args,
    gen_views_dict,
)

if TYPE_CHECKING:
    from glances.plugins.plugin.model import GlancesPluginModel


def _can_update_views(plugin: GlancesPluginModel) -> bool:
    """MemPlugin.update_views() expects 'percent', 'used', 'total' in stats."""
    s = getattr(plugin, 'stats', None)
    if not s or not isinstance(s, dict):
        return False
    return all(k in s for k in ('percent', 'used', 'total'))


def get_executors(plugin: GlancesPluginModel) -> list[tuple[Any, Callable[[], Any]]]:
    """Build a list of (guard, executor) pairs. guard is None (always run) or a callable (plugin) -> bool.
    Do not call update() or get_stats_snmp(). All generators are precondition-safe.
    """
    return [
        # Stats
        (None, make_executor([gen_stats_dict], lambda s: plugin.set_stats(s))),
        (None, make_executor([], lambda: plugin.get_raw())),
        (None, make_executor([], lambda: plugin.get_export())),
        (None, make_executor([], lambda: plugin.get_stats())),
        (None, make_executor([], lambda: plugin.get_json())),
        (None, make_executor([], lambda: plugin.reset())),
        (None, make_executor([], lambda: plugin.get_init_value())),
        # Views (update_views only when stats has percent/used/total for MemPlugin)
        (_can_update_views, make_executor([], lambda: plugin.update_views())),
        (None, make_executor(
            [gen_views_args(plugin)],
            lambda t: plugin.get_views(item=t[0], key=t[1], option=t[2]),
        )),
        (None, make_executor(
            [gen_views_args(plugin)],
            lambda t: plugin.get_json_views(item=t[0], key=t[1], option=t[2]),
        )),
        (None, make_executor([gen_views_dict], lambda v: plugin.set_views(v))),
        (None, make_executor([], lambda: plugin.reset_views())),
        # History (no-op when disabled; safe)
        (None, make_executor([], lambda: plugin.update_stats_history())),
        (None, make_executor([gen_raw_history_item(plugin), gen_nb], lambda item, nb: plugin.get_raw_history(item=item, nb=nb))),
        (None, make_executor([gen_raw_history_item(plugin)], lambda item: plugin.get_export_history(item=item))),
        (None, make_executor([gen_raw_history_item(plugin), gen_nb], lambda item, nb: plugin.get_stats_history(item=item, nb=nb))),
        (None, make_executor([gen_trend_item(plugin), gen_trend_nb], lambda item, nb: plugin.get_trend(item, nb=nb))),
        (None, make_executor([], lambda: plugin.reset_stats_history())),
        # Alert (maximum != 0)
        (None, make_executor(
            [gen_get_alert_current, gen_get_alert_minimum, gen_get_alert_maximum],
            lambda cur, mn, mx: plugin.get_alert(current=cur, minimum=mn, maximum=mx),
        )),
        (None, make_executor(
            [gen_get_alert_current, gen_get_alert_minimum, gen_get_alert_maximum],
            lambda cur, mn, mx: plugin.get_alert_log(current=cur, minimum=mn, maximum=mx),
        )),
        # Accessors
        (None, make_executor([gen_item_for_get(plugin)], lambda item: plugin.get(item, default=None))),
        (None, make_executor([], lambda: plugin.keys())),
        (None, make_executor(
            [gen_item_info_item(plugin), gen_item_info_key],
            lambda item, key: plugin.get_item_info(item, key, default=None),
        )),
        # Limits
        (None, make_executor([gen_limits_item], lambda item: plugin.get_limits(item=item))),
        (None, make_executor([], lambda: plugin.get_limits())),
        (None, make_executor([gen_limits_item, gen_limits_value], lambda item, val: plugin.set_limits(item, val))),
        (None, make_executor([], lambda: plugin.get_refresh())),
        (None, make_executor([], lambda: plugin.get_refresh_time())),
        (None, make_executor([gen_limits_value], lambda v: plugin.set_refresh(v))),
        (None, make_executor([gen_config], lambda c: plugin.load_limits(c))),
        # limits property
        (None, make_executor([], lambda: plugin.limits)),
        (None, make_executor([], lambda: setattr(plugin, 'limits', dict(getattr(plugin, '_limits', {}))))),
        # Other
        (None, make_executor([], lambda: plugin.sorted_stats())),
        (None, make_executor([gen_filter_stats_input(plugin)], lambda s: plugin.filter_stats(s))),
    ]
