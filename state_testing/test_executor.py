#!/usr/bin/env python
#
# Glances - An eye on your system
#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
#
# SPDX-License-Identifier: LGPL-3.0-only
#
# Tests for the executor testing utilities.

"""Tests for state_testing.executor."""

import random
import pytest

from state_testing.executor import make_executor, run_n, run_n_collect


def test_make_executor_calls_function_with_generated_values():
    """Executor calls the function with one value from each generator, in order."""
    calls = []

    def gen1():
        return 1

    def gen2():
        return 2

    def record(a, b):
        calls.append((a, b))
        return a + b

    run = make_executor([gen1, gen2], record)
    assert run() == 3
    assert calls == [(1, 2)]


def test_make_executor_multiple_invocations():
    """Each executor call runs generators again (e.g. new random values)."""
    counter = [0]

    def counting_gen():
        counter[0] += 1
        return counter[0]

    run = make_executor([counting_gen, counting_gen], lambda a, b: (a, b))
    assert run() == (1, 2)
    assert run() == (3, 4)


def test_make_executor_single_generator():
    """Works with a single generator and single-arg function."""
    run = make_executor([lambda: 42], lambda x: x * 2)
    assert run() == 84


def test_make_executor_no_generators():
    """Works with no generators (func called with no args)."""
    run = make_executor([], lambda: 7)
    assert run() == 7


def test_run_n_yields_n_results():
    """run_n yields exactly n results from the executor."""
    run = make_executor([lambda: random.random()], lambda x: x)
    results = list(run_n(run, 5))
    assert len(results) == 5
    assert all(isinstance(r, float) for r in results)


def test_run_n_collect():
    """run_n_collect returns a list of n results."""
    run = make_executor([lambda: 1, lambda: 2], lambda a, b: a + b)
    results = run_n_collect(run, 3)
    assert results == [3, 3, 3]
