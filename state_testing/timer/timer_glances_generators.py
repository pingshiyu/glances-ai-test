#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Random generators for Timer and Counter fuzzer. Each generator is a no-arg
# callable that returns a value satisfying preconditions for the API.
#

import random

# Edge cases and range for duration (Timer.set, Timer.reset, Timer(duration)).
# Non-negative; 0 and small values exercise "already finished" paths.
DURATION_EDGES = [0, 0.0, 1, 1.0, 2, 5, 10, 60, 100.0, 3600]


def gen_duration():
    """Duration for Timer: numeric (int or float), non-negative.
    Covers edge cases (0, 1, small, large) and random values."""
    if random.random() < 0.4:
        return random.choice(DURATION_EDGES)
    if random.random() < 0.5:
        return random.uniform(0.0, 100.0)
    return random.randint(0, 100)


def gen_duration_or_none():
    """Optional duration for Timer.reset(duration=None): None or numeric."""
    if random.random() < 0.4:
        return None
    return gen_duration()


def gen_time_delta():
    """Positive seconds to advance logical time (for advance-then-get/finished executors)."""
    if random.random() < 0.3:
        return 0.0
    if random.random() < 0.5:
        return random.uniform(0.1, 10.0)
    return random.uniform(10.0, 200.0)
