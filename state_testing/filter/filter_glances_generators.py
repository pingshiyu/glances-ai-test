#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Random generators for GlancesFilterList fuzzer. Each generator is a no-arg
# callable that returns a value satisfying preconditions for the API.
#

import random
import string

# Single filter segments that are valid regexes (compile successfully).
# Mix of plain patterns and key:pattern form; all compile.
SAFE_FILTER_SEGMENTS = [
    "",
    ".*",
    ".",
    "a",
    "python",
    "python.*",
    ".*python.*",
    "[a-z]+",
    "[0-9]+",
    "username:nicolargo",
    "user:nicolargo",
    "username:.*nico.*",
    "name:python",
    "cmdline:.*",
]


def _safe_regex_fragment() -> str:
    """Build a short regex fragment from safe characters (no unclosed brackets)."""
    chars = string.ascii_lowercase + string.digits + ".*"
    return "".join(random.choices(chars, k=random.randint(1, 8)))


def gen_filter_string() -> str:
    """Filter string for filter setter: comma-separated list of segments that compile as regex.
    Prefer single segment to limit list growth; occasionally 2-3 segments."""
    if random.random() < 0.7:
        # Single segment
        if random.random() < 0.8:
            return random.choice(SAFE_FILTER_SEGMENTS)
        return _safe_regex_fragment()
    # 2-3 segments
    n = random.randint(2, 3)
    segments = [
        random.choice(SAFE_FILTER_SEGMENTS) if random.random() < 0.7 else _safe_regex_fragment()
        for _ in range(n)
    ]
    return ",".join(segments)


def gen_process_dict() -> dict:
    """Process dict for is_filtered(process). Keys: name, cmdline, username, etc.
    Values are str or list of str; include empty dict, minimal, and richer dicts."""
    choice = random.choice(["empty", "minimal_name", "minimal_cmdline", "both", "rich", "with_key"])
    if choice == "empty":
        return {}
    if choice == "minimal_name":
        return {"name": _random_str_or_none()}
    if choice == "minimal_cmdline":
        return {"cmdline": _random_cmdline_value()}
    if choice == "both":
        return {
            "name": _random_str_or_none(),
            "cmdline": _random_cmdline_value(),
        }
    if choice == "rich":
        return {
            "name": _random_str_or_none(),
            "cmdline": _random_cmdline_value(),
            "username": _random_str_or_none() if random.random() < 0.5 else None,
        }
    # with_key: include custom key for key:pattern filters
    d = {
        "name": _random_str_or_none(),
        "cmdline": _random_cmdline_value(),
    }
    if random.random() < 0.5:
        d["username"] = _random_str_or_none()
    if random.random() < 0.3:
        d["user"] = _random_str_or_none()
    return d


def _random_str_or_none() -> str | None:
    """Short string or occasionally None for edge cases."""
    if random.random() < 0.1:
        return None
    chars = string.ascii_lowercase + string.digits + " "
    return "".join(random.choices(chars, k=random.randint(0, 12)))


def _random_cmdline_value() -> str | list:
    """cmdline can be string or list of strings (implementation handles both)."""
    if random.random() < 0.5:
        return _random_str_or_none() or ""
    n = random.randint(0, 4)
    if n == 0:
        return []
    return [_random_str_or_none() or "" for _ in range(n)]
