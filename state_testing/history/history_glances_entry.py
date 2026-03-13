#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Entry point for the GlancesHistory state-based fuzzer. Runs a random
# sequence of API calls for 1000 iterations.
#

import random

from ._glances_loader import GlancesHistory

from .history_glances_lib import get_executors


def dummyTester() -> None:
    """Run the fuzzer: 1000 iterations, each iteration picks a random executor and runs it."""
    history = GlancesHistory()
    executors = get_executors(history)
    for _ in range(1000):
        run = random.choice(executors)
        run()


if __name__ == "__main__":
    dummyTester()
