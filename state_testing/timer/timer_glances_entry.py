#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Entry point for the Timer and Counter state-based fuzzer. Runs a random
# sequence of API calls for 1000 iterations with mocked time.
#

import os
import random
from unittest.mock import patch

# Direct Glances logger to a writable path before any glances import.
_cache = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".cache"))
os.makedirs(_cache, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", _cache)

from .timer_glances_generators import gen_duration
from .timer_glances_lib import _make_fake_datetime, get_executors


def dummyTester() -> None:
    """Run the fuzzer: 1000 iterations with mocked time, each iteration picks a random executor and runs it."""
    logical_time = [1000.0]

    def time_getter():
        return logical_time[0]

    with patch("glances.timer.time", side_effect=time_getter):
        with patch("glances.timer.datetime", _make_fake_datetime(time_getter)):
            from glances.timer import Counter, Timer

            timer = Timer(gen_duration())
            counter = Counter()
            executors = get_executors(timer, counter, logical_time)
            for _ in range(1000):
                logical_time[0] = 1000.0
                run = random.choice(executors)
                run()


if __name__ == "__main__":
    dummyTester()
