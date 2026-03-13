#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Pytest entry for GlancesHistory fuzzer: runs dummyTester (1000 iterations).
#

import pytest

from state_testing.history.history_glances_entry import dummyTester


def test_history_fuzzer_1000_iterations():
    """Run the GlancesHistory state-based fuzzer for 1000 iterations (success = no crash)."""
    dummyTester()
