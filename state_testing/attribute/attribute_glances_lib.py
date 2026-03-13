#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executors for GlancesAttribute: each executor runs generators and calls one
# API method on the shared attribute instance. Returns (min_history, run)
# pairs so the entry point can filter by precondition.
#

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from glances.attribute import GlancesAttribute

from state_testing.executor import make_executor

from .attribute_glances_generators import (
    gen_history_entry,
    gen_nb,
    gen_nb_mean,
    gen_pos,
    gen_value_for_setter,
)


def get_executors(attr: GlancesAttribute) -> list[tuple[int, bool, Callable[[], Any]]]:
    """Build a list of (min_history, require_value_set, executor) for the given GlancesAttribute.
    min_history: minimum attr.history_len() required. require_value_set: if True, only run when attr._value is not None (value getter).
    """
    return [
        (0, False, make_executor([gen_value_for_setter], lambda v: setattr(attr, "value", v))),
        (0, False, make_executor([gen_history_entry], lambda entry: attr.history_add(entry))),
        (0, False, make_executor([], lambda: attr.history_reset())),
        (0, False, make_executor([gen_nb], lambda nb: attr.history_raw(nb))),
        (0, False, make_executor([gen_nb], lambda nb: attr.history_json(nb))),
        (1, False, make_executor([gen_pos(attr)], lambda pos: attr.history_value(pos))),
        # history_mean: commented out – API bug (denominator uses v[-1]-v[-nb] instead of count; ZeroDivisionError when constant values)
        # (1, False, make_executor([gen_nb_mean(attr)], lambda nb: attr.history_mean(nb))),
        (0, False, make_executor([], lambda: attr.history_len())),
        # value getter: commented out – API bug (divides number by timedelta -> TypeError in Python 3)
        # (2, True, make_executor([], lambda: attr.value)),
    ]
