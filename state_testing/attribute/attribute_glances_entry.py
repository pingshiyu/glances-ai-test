#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Entry point for the GlancesAttribute state-based fuzzer. Runs a random
# sequence of API calls for 1000 iterations.
#

import random

from glances.attribute import GlancesAttribute

from .attribute_glances_lib import get_executors


def dummyTester() -> None:
    """Run the fuzzer: 1000 iterations, each iteration picks a random executor and runs it."""
    # history_max_size must be set so that value setter and history_add actually append
    attr = GlancesAttribute("fuzz", description="", history_max_size=100)
    executors = get_executors(attr)
    for _ in range(1000):
        candidates = [
            run
            for (mh, require_value_set, run) in executors
            if attr.history_len() >= mh and (not require_value_set or getattr(attr, "_value", None) is not None)
        ]
        run = random.choice(candidates)
        run()


if __name__ == "__main__":
    dummyTester()
