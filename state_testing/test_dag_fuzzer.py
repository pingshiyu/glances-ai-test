#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Pytest entry for get_plugin_dependencies (dag) fuzzer: runs dummyTester (1000 iterations).
#

import pytest

from state_testing.dag.dag_entry import dummyTester


def test_dag_fuzzer_1000_iterations():
    """Run the get_plugin_dependencies state-based fuzzer for 1000 iterations (success = no crash)."""
    dummyTester()
