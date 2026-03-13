#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Regression tests for GlancesAttribute API crashes documented in
# state_testing/attribute/working_semantics.md (Crashes section).
#

"""Tests that replicate fuzzer-discovered crashes in GlancesAttribute API."""

import importlib.util
import os
import pytest

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc  # type: ignore[assignment]
from datetime import datetime


def _load_GlancesAttribute():
    """Load GlancesAttribute from glances/attribute.py so tests run without glances package (psutil)."""
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "glances", "attribute.py"))
    spec = importlib.util.spec_from_file_location("glances_attribute", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.GlancesAttribute


GlancesAttribute = _load_GlancesAttribute()


# --- Crash 1: history_mean(nb) – ZeroDivisionError when constant values ---


def test_history_mean_zerodivision_when_constant_values():
    """history_mean(nb) raises ZeroDivisionError when v[-1] == v[-nb] (constant values).

    Implementation uses denominator float(v[-1] - v[-nb]); when all values in the
    slice are equal this is zero. Documented in working_semantics.md.
    """
    attr = GlancesAttribute("fuzz", description="", history_max_size=10)
    # Fill history with same value so v[-1] - v[-nb] == 0
    base_ts = datetime.now(UTC)
    for i in range(5):
        attr.history_add((base_ts, 42))
    assert attr.history_len() >= 1
    with pytest.raises(ZeroDivisionError):
        attr.history_mean(nb=5)


# --- Crash 2: value getter – TypeError (int/timedelta) and NoneType not subscriptable ---


def test_value_getter_typeerror_int_div_timedelta():
    """value getter raises TypeError: unsupported operand type(s) for /: 'int' and 'datetime.timedelta'.

    Getter computes (self._value[1] - self.history_value()[1]) / (self._value[0] - self.history_value()[0]).
    When _value is not the last history entry, denominator is a timedelta; Python 3 does not support number / timedelta.
    Trigger: set value then history_add another entry so _value != _history[-1].
    """
    attr = GlancesAttribute("fuzz", description="", history_max_size=10)
    attr.value = 10
    # Add another entry so last in history is not _value
    attr.history_add((datetime.now(UTC), 20))
    assert attr.history_len() >= 2
    with pytest.raises(TypeError, match="unsupported operand type.*for /.*int.*timedelta"):
        _ = attr.value


def test_value_getter_none_type_when_only_history_add():
    """value getter crashes with NoneType not subscriptable when only history_add was used (no value setter).

    _value is only set by the value setter. If history was populated only via history_add,
    _value stays None and the getter does self._value[1] -> TypeError.
    """
    attr = GlancesAttribute("fuzz", description="", history_max_size=10)
    attr.history_add((datetime.now(UTC), 5))
    assert attr.history_len() == 1
    assert attr._value is None
    with pytest.raises(TypeError, match="'NoneType' object is not subscriptable"):
        _ = attr.value
