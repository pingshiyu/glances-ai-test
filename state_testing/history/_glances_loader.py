#
# Load glances.history and glances.attribute without running glances/__init__.py
# (which requires psutil and sys.exit). Allows the fuzzer to run without psutil.
#

import importlib.util
import sys
from pathlib import Path

# Project root (parent of state_testing)
_root = Path(__file__).resolve().parent.parent.parent
_glances_dir = _root / "glances"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Ensure minimal 'glances' package exists so "from glances.attribute import ..." works
if "glances" not in sys.modules:
    import types
    sys.modules["glances"] = types.ModuleType("glances")

# Load attribute first (history imports it)
_load_module("glances.attribute", _glances_dir / "attribute.py")
_load_module("glances.history", _glances_dir / "history.py")

GlancesHistory = sys.modules["glances.history"].GlancesHistory
