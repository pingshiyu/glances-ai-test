#
# Glances - An eye on your system
#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
#
# SPDX-License-Identifier: LGPL-3.0-only
#
# Run state_testing's own tests when invoked as: python -m state_testing

"""Run state_testing tests via python -m state_testing."""

import os
import sys

import pytest


if __name__ == "__main__":
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    sys.exit(pytest.main(["-v", pkg_dir]))
