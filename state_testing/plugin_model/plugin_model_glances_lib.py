#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executors for GlancesPluginModel (mem plugin): each executor runs generators
# and calls one API method on the shared instance. Full logic coverage.
#

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from state_testing.executor import make_executor

from .plugin_model_glances_generators import (
    gen_action_key,
    gen_current,
    gen_header,
    gen_is_max,
    gen_limits_item_or_none,
    gen_limits_value,
    gen_log,
    gen_maximum,
    gen_mem_stats,
    gen_minimum,
    gen_mock_config,
    gen_set_limits_pair,
    gen_stat_name,
    gen_trigger,
    gen_views_args,
    gen_highlight_zero,
)


def get_executors(sut: Any) -> list[Callable[[], Any]]:
    """Build a list of executors that operate on the given plugin instance."""
    return [
        make_executor([gen_mem_stats], lambda stats: sut.set_stats(stats)),
        make_executor([], lambda: sut.update_views()),
        make_executor([], lambda: sut.update_stats_history()),
        make_executor(
            [lambda: gen_views_args(sut)()],
            lambda t: sut.get_views(t[0], t[1], t[2]),
        ),
        make_executor([], lambda: sut.get_raw()),
        make_executor([], lambda: sut.get_export()),
        make_executor(
            [
                gen_current,
                gen_minimum,
                gen_maximum,
                gen_highlight_zero,
                gen_is_max,
                gen_header,
                gen_action_key,
                gen_log,
            ],
            lambda c, mi, ma, hz, im, h, ak, log: sut.get_alert(
                current=c, minimum=mi, maximum=ma, highlight_zero=hz,
                is_max=im, header=h, action_key=ak, log=log,
            ),
        ),
        make_executor(
            [gen_current, gen_minimum, gen_maximum, gen_header, gen_action_key],
            lambda c, mi, ma, h, ak: sut.get_alert_log(
                current=c, minimum=mi, maximum=ma, header=h or '', action_key=ak,
            ),
        ),
        make_executor(
            [gen_set_limits_pair],
            lambda pair: sut.set_limits(pair[0], pair[1]),
        ),
        make_executor([gen_mock_config], lambda config: sut.load_limits(config)),
        make_executor([gen_stat_name, gen_trigger], lambda sn, t: sut.manage_threshold(sn, t)),
        make_executor(
            [gen_stat_name, gen_trigger, gen_header, gen_action_key],
            lambda sn, t, h, ak: sut.manage_action(sn, t, h, ak),
        ),
        make_executor([], lambda: sut.reset()),
        make_executor([gen_limits_item_or_none], lambda item: sut.get_limits(item=item)),
    ]
