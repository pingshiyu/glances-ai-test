#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
# SPDX-License-Identifier: LGPL-3.0-only
#
# Random generators for get_plugin_dependencies fuzzer. Each generator is a
# no-arg callable that returns a value satisfying preconditions for the API.
#

import random
import string

# Plugin names from the default _plugins_graph (for "in graph" coverage).
DEFAULT_GRAPH_PLUGINS = [
    "*",
    "alert",
    "cpu",
    "core",
    "load",
    "processlist",
    "processcount",
    "programlist",
    "quicklook",
    "fs",
    "vms",
]


def _random_plugin_name() -> str:
    """Short alphanumeric string, possibly with underscore."""
    chars = string.ascii_lowercase + string.digits + "_"
    length = random.randint(0, 12)
    return "".join(random.choices(chars, k=length))


def gen_plugin_name() -> str:
    """Plugin name: mix of known names from default graph, random names, empty string."""
    choice = random.choice(["known", "known", "random", "random", "empty"])
    if choice == "known":
        return random.choice(DEFAULT_GRAPH_PLUGINS)
    if choice == "random":
        return _random_plugin_name()
    return ""


def gen_graph() -> dict[str, list[str]]:
    """Dependency graph: dict[str, list[str]]. Edge cases and random graphs."""
    choice = random.choice([
        "empty",
        "star_empty",
        "star_one",
        "single_node",
        "chain",
        "cycle",
        "deep_chain",
        "random",
    ])
    if choice == "empty":
        return {}
    if choice == "star_empty":
        return {"*": []}
    if choice == "star_one":
        return {"*": [random.choice(["x", "alert", "common"])]}
    if choice == "single_node":
        return {"a": []}
    if choice == "chain":
        return {"a": ["b"], "b": ["c"], "c": []}
    if choice == "cycle":
        return {"a": ["b"], "b": ["a"]}
    if choice == "deep_chain":
        return {"a": ["b"], "b": ["c"], "c": ["d"], "d": []}
    # random: a few nodes, each with 0–2 deps from a small alphabet
    nodes = ["*", "a", "b", "c", "d", "e"][: random.randint(2, 6)]
    graph = {}
    for n in nodes:
        k = random.randint(0, 2)
        deps = random.sample([x for x in nodes if x != n], min(k, len(nodes) - 1))
        graph[n] = deps if deps else []
    return graph
