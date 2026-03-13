#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Random generators for GlancesAttribute fuzzer. Each generator is a no-arg
# callable (or a factory returning one) that returns values satisfying
# preconditions for the API.
#

import random
from collections.abc import Callable
from typing import Any

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc  # type: ignore[assignment]
from datetime import datetime


def gen_value_for_setter() -> int | float:
    """Value for value setter: int or float, including 0 and negative."""
    choice = random.choice(["int", "float", "zero", "negative"])
    if choice == "int":
        return random.randint(-1000, 1000)
    if choice == "float":
        return random.uniform(-100.0, 100.0)
    if choice == "zero":
        return random.choice([0, 0.0])
    return random.choice([-1, -1.0, -100])


def gen_history_entry() -> tuple[datetime, int | float]:
    """Single history entry (timestamp, value) for history_add."""
    x = gen_value_for_setter()
    return (datetime.now(UTC), x)


def gen_nb() -> int:
    """nb for history_raw/history_json: non-negative int. Safe for slicing."""
    if random.random() < 0.3:
        return 0
    return random.randint(0, 500)


def gen_pos(attr: Any) -> Callable[[], int]:
    """Factory: returns a no-arg callable that yields pos in 1..attr.history_len().
    Call only when attr.history_len() >= 1.
    """
    def f() -> int:
        L = attr.history_len()
        return random.randint(1, max(1, L))
    return f


def gen_nb_mean(attr: Any) -> Callable[[], int]:
    """Factory: returns a no-arg callable that yields nb in 1..min(L, 5) for history_mean.
    Call only when attr.history_len() >= 1. Known bug in history_mean (wrong denominator)."""
    def f() -> int:
        L = attr.history_len()
        return random.randint(1, min(max(1, L), 5))
    return f
