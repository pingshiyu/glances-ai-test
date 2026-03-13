#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Pytest entry for GlancesPluginModel (view/history/alert) fuzzer: runs dummyTester (1000 iterations).
#

import pytest

from state_testing.plugin_model.plugin_model_glances_entry import dummyTester


def test_plugin_model_fuzzer_1000_iterations():
    """Run the GlancesPluginModel state-based fuzzer for 1000 iterations (success = no crash)."""
    dummyTester()
