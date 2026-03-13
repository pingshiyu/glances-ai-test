#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Random generators for GlancesHistory fuzzer. Each generator is a no-arg
# callable that returns a value satisfying preconditions for the API.
#

import random
import string


def gen_key():
    """Key for add(): short alphanumeric string, including empty and single-char."""
    choices = [
        "",
        "a",
        "x",
        "cpu",
        "mem",
        "load",
        "stat_name",
        "".join(random.choices(string.ascii_lowercase, k=random.randint(0, 12))),
    ]
    return random.choice(choices)


def gen_value():
    """Value for add(): int or float, including 0 and negative."""
    choice = random.choice(["int", "float", "zero", "negative"])
    if choice == "int":
        return random.randint(-1000, 1000)
    if choice == "float":
        return random.uniform(-100.0, 100.0)
    if choice == "zero":
        return random.choice([0, 0.0])
    return random.choice([-1, -1.0, -100])


def gen_description():
    """Description for add(): string, often empty."""
    if random.random() < 0.5:
        return ""
    return random.choice(["", "CPU usage", "Memory", "a" * 20])


def gen_history_max_size():
    """history_max_size for add(): None or small positive int."""
    if random.random() < 0.4:
        return None
    return random.choice([1, 2, 5, 10, 100])


def gen_nb():
    """nb for get()/get_json(): non-negative int. Covers 0 and large values."""
    if random.random() < 0.3:
        return 0
    return random.randint(0, 500)
