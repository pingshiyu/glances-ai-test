#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executors for get_plugin_dependencies: each executor runs generators and
# calls the API (pure function, no SUT instance).
#

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from glances.plugins.plugin.dag import get_plugin_dependencies

from state_testing.executor import make_executor

from .dag_generators import gen_plugin_name, gen_graph


def get_executors() -> list[Callable[[], Any]]:
    """Build a list of executors for get_plugin_dependencies (no SUT)."""
    return [
        make_executor(
            [gen_plugin_name],
            lambda name: get_plugin_dependencies(name),
        ),
        make_executor(
            [gen_plugin_name, gen_graph],
            lambda name, graph: get_plugin_dependencies(name, graph),
        ),
    ]
