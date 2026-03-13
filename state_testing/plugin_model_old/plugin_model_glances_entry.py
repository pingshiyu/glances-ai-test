#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Entry point for the GlancesPluginModel (view/history/alert) state-based fuzzer.
# Runs a random sequence of API calls for 1000 iterations. Do not call update() or get_stats_snmp().
#

import os
import random

# Direct Glances logger/cache to a writable path before any glances import.
_cache = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".cache"))
os.makedirs(_cache, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", _cache)

from glances.plugins.mem import MemPlugin

from .plugin_model_glances_lib import get_executors


def _make_args():
    """Minimal args namespace: disable_history to simplify; time for get_refresh."""
    from types import SimpleNamespace
    return SimpleNamespace(disable_history=True, time=2)


def dummyTester() -> None:
    """Run the fuzzer: 1000 iterations, each iteration picks a random executor and runs it."""
    args = _make_args()
    config = None
    plugin = MemPlugin(args=args, config=config)
    executor_list = get_executors(plugin)
    for _ in range(1000):
        candidates = [
            run for (guard, run) in executor_list
            if guard is None or guard(plugin)
        ]
        run = random.choice(candidates)
        run()


if __name__ == "__main__":
    dummyTester()
