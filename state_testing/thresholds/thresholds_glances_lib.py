#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executors for GlancesThresholds: each executor runs generators and calls one
# API method on the shared instance.
#

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from glances.thresholds import GlancesThresholds

from state_testing.executor import make_executor

from .thresholds_glances_generators import (
    gen_stat_name,
    gen_stat_name_or_none,
    gen_threshold_description,
)


def get_executors(sut: GlancesThresholds) -> list[Callable[[], Any]]:
    """Build a list of executors that operate on the given GlancesThresholds instance."""
    return [
        make_executor(
            [gen_stat_name, gen_threshold_description],
            lambda stat_name, threshold_description: sut.add(stat_name, threshold_description),
        ),
        make_executor(
            [gen_stat_name_or_none],
            lambda stat_name: sut.get(stat_name),
        ),
    ]
