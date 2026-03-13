#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executors for GlancesHistory: each executor runs generators and calls one
# API method on the shared history instance.
#

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from glances.history import GlancesHistory

from state_testing.executor import make_executor

from .history_glances_generators import (
    gen_description,
    gen_history_max_size,
    gen_key,
    gen_nb,
    gen_value,
)


def get_executors(history: GlancesHistory) -> list[Callable[[], Any]]:
    """Build a list of executors that operate on the given GlancesHistory instance."""
    return [
        make_executor(
            [gen_key, gen_value, gen_description, gen_history_max_size],
            lambda k, v, d, m: history.add(k, v, description=d, history_max_size=m),
        ),
        make_executor([], lambda: history.reset()),
        make_executor([gen_nb], lambda nb: history.get(nb)),
        make_executor([gen_nb], lambda nb: history.get_json(nb)),
    ]
