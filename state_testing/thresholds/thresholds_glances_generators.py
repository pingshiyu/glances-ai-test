#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Random generators for GlancesThresholds fuzzer. Each generator is a no-arg
# callable that returns a value satisfying preconditions for the API.
#

import random
import string

# Must match GlancesThresholds.threshold_list exactly (precondition for add()).
THRESHOLD_LIST = ['OK', 'CAREFUL', 'WARNING', 'CRITICAL']


def gen_stat_name():
    """Stat name for add()/get(): mix of edge cases and random strings."""
    choices = [
        "",
        "a",
        "x",
        "cpu",
        "cpu_user",
        "mem",
        "load",
        "stat_name",
        "disk",
        "network",
        "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(0, 15))),
    ]
    return random.choice(choices)


def gen_threshold_description():
    """Threshold description for add(): only valid values (exact case)."""
    return random.choice(THRESHOLD_LIST)


def gen_stat_name_or_none():
    """For get(stat_name=None): either None (get all) or a stat name string."""
    if random.random() < 0.3:
        return None
    return gen_stat_name()
