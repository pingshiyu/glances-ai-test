#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Entry point for the GlancesPluginModel (mem plugin) state-based fuzzer.
# Runs a random sequence of API calls for 5000 iterations with mocks.
#

import os
import random
from unittest.mock import MagicMock, patch

# Direct Glances logger to a writable path before any glances import.
_cache = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".cache"))
os.makedirs(_cache, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", _cache)

# Patch before any glances import so events and secure_popen are no-ops.
_mock_events = MagicMock()
_mock_events.add = MagicMock(return_value=None)
patch("glances.events_list.glances_events", _mock_events).start()
patch("glances.secure.secure_popen", MagicMock(return_value="")).start()

from glances.plugins.mem import MemPlugin

from .plugin_model_glances_lib import get_executors


def _make_args():
    """Minimal args namespace for MemPlugin: disable_mem, disable_history, time."""
    ns = type("Args", (), {})()
    ns.disable_mem = False
    ns.disable_history = False
    ns.time = 2
    return ns


def dummyTester() -> None:
    """Run the fuzzer: 5000 iterations, each iteration picks a random executor and runs it."""
    args = _make_args()
    sut = MemPlugin(args=args, config=None)
    sut._limits.setdefault("history_size", 28800)
    executors = get_executors(sut)
    for _ in range(5000):
        run = random.choice(executors)
        run()


if __name__ == "__main__":
    dummyTester()
