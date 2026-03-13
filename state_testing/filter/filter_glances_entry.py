#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Entry point for the GlancesFilterList state-based fuzzer. Runs a random
# sequence of API calls for 1000 iterations.
#

import os
import random

# Direct Glances logger to a writable path before any glances import.
_cache = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".cache"))
os.makedirs(_cache, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", _cache)

from glances.filter import GlancesFilterList

from .filter_glances_lib import get_executors


def dummyTester() -> None:
    """Run the fuzzer: 1000 iterations, each iteration picks a random executor and runs it."""
    sut = GlancesFilterList()
    executors = get_executors(sut)
    for _ in range(1000):
        run = random.choice(executors)
        run()


if __name__ == "__main__":
    dummyTester()
