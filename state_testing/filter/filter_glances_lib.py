#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executors for GlancesFilterList: each executor runs generators and calls one
# API method on the shared instance.
#

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from glances.filter import GlancesFilterList

from state_testing.executor import make_executor

from .filter_glances_generators import gen_filter_string, gen_process_dict


def get_executors(sut: GlancesFilterList) -> list[Callable[[], Any]]:
    """Build a list of executors that operate on the given GlancesFilterList instance."""
    return [
        make_executor(
            [gen_filter_string],
            lambda s: setattr(sut, "filter", s),
        ),
        make_executor(
            [],
            lambda: sut.filter,
        ),
        make_executor(
            [gen_process_dict],
            lambda process: sut.is_filtered(process),
        ),
    ]
