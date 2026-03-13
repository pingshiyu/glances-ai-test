#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Pytest entry for GlancesFilterList fuzzer: runs dummyTester (1000 iterations).
#

import pytest

from state_testing.filter.filter_glances_entry import dummyTester


def test_filter_fuzzer_1000_iterations():
    """Run the GlancesFilterList state-based fuzzer for 1000 iterations (success = no crash)."""
    dummyTester()
