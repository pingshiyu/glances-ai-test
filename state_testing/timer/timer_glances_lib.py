#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Executors for Timer and Counter: each executor runs with mocked time and
# calls one API method on the shared Timer or Counter instance.
#

from __future__ import annotations

from datetime import datetime as real_datetime

from state_testing.executor import make_executor

from .timer_glances_generators import (
    gen_duration,
    gen_duration_or_none,
    gen_time_delta,
)


def _make_fake_datetime(time_getter):
    """Return an object that has .now() returning datetime.fromtimestamp(time_getter())."""

    class FakeDatetime:
        @staticmethod
        def now():
            return real_datetime.fromtimestamp(time_getter())

    return FakeDatetime


def get_executors(sut_timer, sut_counter, logical_time_list):
    """Build a list of executors that operate on the given Timer and Counter.

    logical_time_list: mutable list of one float (e.g. [1000.0]). The caller
    must patch glances.timer.time and glances.timer.datetime so that they read
    from this list. Each executor may advance logical_time_list[0] for
    advance-then-get/finished executors.
    """
    T = logical_time_list

    # All executors assume patches are already active (entry point installs them).
    # Generators are called at executor invocation time, so they see current T.

    executors = [
        make_executor(
            [gen_duration],
            lambda duration: sut_timer.set(duration),
        ),
        make_executor(
            [gen_duration_or_none],
            lambda duration: sut_timer.reset(duration),
        ),
        make_executor(
            [],
            lambda: sut_timer.start(),
        ),
        make_executor(
            [],
            lambda: sut_timer.get(),
        ),
        make_executor(
            [],
            lambda: sut_timer.finished(),
        ),
        make_executor(
            [gen_time_delta],
            lambda delta: (_advance(T, delta), sut_timer.get())[1],
        ),
        make_executor(
            [gen_time_delta],
            lambda delta: (_advance(T, delta), sut_timer.finished())[1],
        ),
        make_executor(
            [],
            lambda: sut_counter.start(),
        ),
        make_executor(
            [],
            lambda: sut_counter.reset(),
        ),
        make_executor(
            [],
            lambda: sut_counter.get(),
        ),
    ]
    return executors


def _advance(logical_time_list, delta):
    logical_time_list[0] += delta
