#!/usr/bin/env python
#
# Glances - An eye on your system
#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
#
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executor utilities for property/state-based testing: run a function with
# randomly generated inputs from a list of generator callables.

"""Executor for testing: run a function with values from input generators."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def make_executor(
    generators: Iterable[Callable[[], T]],
    func: Callable[..., R],
) -> Callable[[], R]:
    """
    Build an executor that generates one value from each generator and calls
    func with those values (in order).

    Generators are callables that take no arguments and return a value (e.g. a
    random value from some set). The returned executor takes no arguments;
    when called it runs each generator once, then calls func with the
    generated values as positional arguments.

    Example:
        def gen_int():
            return random.randint(0, 10)

        def add(a: int, b: int) -> int:
            return a + b

        run = make_executor([gen_int, gen_int], add)
        result = run()  # add(gen_int(), gen_int())
    """
    gen_list = list(generators)

    def executor() -> R:
        values = [g() for g in gen_list]
        return func(*values)

    return executor


def run_n(
    executor: Callable[[], R],
    n: int,
) -> Iterator[R]:
    """
    Run the executor n times and yield each return value.

    Useful for fuzzing loops or collecting outcomes for assertions.
    """
    for _ in range(n):
        yield executor()


def run_n_collect(
    executor: Callable[[], R],
    n: int,
) -> list[R]:
    """Run the executor n times and return a list of results."""
    return list(run_n(executor, n))
