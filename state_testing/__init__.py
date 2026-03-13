#
# Glances - An eye on your system
#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
#
# SPDX-License-Identifier: LGPL-3.0-only
#
# State-based / property-based testing utilities (executor, generators).
# Independent from the main tests suite.

"""State testing framework: run functions with generated inputs."""

from state_testing.executor import make_executor, run_n, run_n_collect

__all__ = ["make_executor", "run_n", "run_n_collect"]
