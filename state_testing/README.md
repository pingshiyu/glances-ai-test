# State testing framework

Independent package for state-based / property-based testing. It provides an **executor**: a callable that, when invoked, draws one value from each of a list of **generators** and calls a **target function** with those values (in order). This is the basis for fuzzing and random testing of APIs.

**Audience:** This document tells you how to use the framework as an agent or developer: how to write tests that use the executor, and how to run existing or new tests.

---

## SUT environment (running the system under test with full dependencies)

To run the **system under test** (Glances) with all dependencies (e.g. `psutil`) satisfied, create and activate a dedicated virtual environment from the **project root**:

**With uv:**
```bash
uv venv .venv-sut && source .venv-sut/bin/activate   # Linux/macOS
# or:  .venv-sut\Scripts\activate                    # Windows
uv pip install -e .
```

**With standard Python:**
```bash
python -m venv .venv-sut && source .venv-sut/bin/activate   # Linux/macOS
# or:  .venv-sut\Scripts\activate                            # Windows
pip install -e .
```

Then run fuzzers or tests from the project root. The executor tests and some fuzzers (e.g. GlancesHistory) can also run without this environment by loading only the needed modules; use this environment when you need the full Glances package to import normally.

---

## Concepts

- **Generator:** A callable that takes **no arguments** and returns a value (e.g. from a set of possible inputs). Each call can return a different value (e.g. random). Example: `lambda: random.randint(0, 10)`.
- **Target function:** The function under test. It must accept as many **positional** arguments as there are generators; they are passed in the same order as the generator list.
- **Executor:** A callable (returned by `make_executor`) that takes no arguments. When called, it runs each generator once, then calls the target function with the generated values and returns its return value.

---

## API reference

Import from the package:

```python
from state_testing import make_executor, run_n, run_n_collect
```

### `make_executor(generators, func)`

- **Parameters:**
  - `generators`: Iterable of callables with signature `() -> T` (no arguments, return one value). Can be a list, tuple, etc.
  - `func`: Callable that will be called with one value per generator, as positional arguments: `func(*values)`.
- **Returns:** A callable with signature `() -> R`, where `R` is the return type of `func`. No arguments.
- **Behaviour:** Each time the returned executor is called, every generator is invoked once (in order), then `func` is called with those values. So each call can see new “random” inputs.

### `run_n(executor, n)`

- **Parameters:** `executor` (a callable `() -> R`), `n` (non-negative integer).
- **Returns:** An iterator that yields the return value of `executor()` exactly `n` times.
- **Use case:** Fuzzing loops where you run the executor many times and assert or collect outcomes.

### `run_n_collect(executor, n)`

- **Parameters:** Same as `run_n`.
- **Returns:** A list of the `n` return values from calling `executor()`.
- **Use case:** When you need all results in memory (e.g. to assert on the list).

---

## Writing your own tests

### 1. Add a test module under `state_testing/`

- Put test files in the **`state_testing/`** directory (same level as `executor.py` and `test_executor.py`).
- Name test modules so pytest will collect them (e.g. `test_*.py` or `*_test.py` depending on project config). The existing tests use `test_executor.py`; for a new component use e.g. `test_my_component.py`.

### 2. Define generators

Each generator is a no-arg callable that returns one value for the target function:

```python
import random

def gen_int():
    return random.randint(0, 100)

def gen_choice():
    return random.choice(["a", "b", "c"])
```

Ensure the generated values satisfy any preconditions of the function under test (e.g. non-negative, bounded, valid enum).

### 3. Create an executor and use it in a test

```python
from state_testing import make_executor, run_n, run_n_collect

def my_api(a: int, b: str) -> str:
    return f"{a}-{b}"

def test_my_api_smoke():
    run = make_executor([gen_int, gen_choice], my_api)
    result = run()
    assert "-" in result
    assert result.split("-")[0].isdigit()

def test_my_api_many_times():
    run = make_executor([gen_int, gen_choice], my_api)
    results = run_n_collect(run, 100)
    assert len(results) == 100
    for r in results:
        assert isinstance(r, str)
```

### 4. Fuzzing loop pattern

To run the executor many times and assert a property on each outcome (or let exceptions surface):

```python
def test_my_api_no_crashes():
    run = make_executor([gen_int, gen_choice], my_api)
    for outcome in run_n(run, 1000):
        assert outcome is not None  # or your invariant
```

### 5. Matching generators to the target function

- The number of generators must equal the number of **positional** parameters of the target function (or the number of arguments you intend to pass; the executor uses `func(*values)`).
- Order is important: the first generator’s value is the first argument, and so on.

Example with three arguments:

```python
run = make_executor([gen_a, gen_b, gen_c], func_three_args)
# Each run() does: func_three_args(gen_a(), gen_b(), gen_c())
```

---

## Running tests

All commands below are intended to be run from the **project root** (the directory that contains `state_testing/` and `glances/`).

### Run all tests in this package only

```bash
python -m state_testing
```

or:

```bash
pytest state_testing/ -v
```

This runs every test under `state_testing/` (including `test_executor.py` and any new `test_*.py` modules you add). It does **not** require the rest of the Glances test suite or psutil.

### Run a single test file

```bash
pytest state_testing/test_executor.py -v
pytest state_testing/test_my_component.py -v
```

### Run a single test by name

```bash
pytest state_testing/test_executor.py::test_make_executor_calls_function_with_generated_values -v
```

### Run tests from Python

```python
import pytest
# Run only the state_testing package
pytest.main(["-v", "state_testing"])
```

---

## File layout (for adding tests)

```
state_testing/
├── README.md           # This file
├── __init__.py         # Exports make_executor, run_n, run_n_collect
├── __main__.py         # Entry point for python -m state_testing
├── executor.py         # Implementation of make_executor, run_n, run_n_collect
├── test_executor.py    # Tests for the executor itself
└── test_<your>.py      # Add new test modules here
```

To add tests: create a new `test_*.py` under `state_testing/`, import `make_executor` (and optionally `run_n` / `run_n_collect`) from `state_testing`, define generators and target functions, and use the patterns above. No need to modify `executor.py` or `__init__.py` unless you are extending the API.

---

## Minimal copy-paste example

```python
# state_testing/test_example.py
import random
import pytest
from state_testing import make_executor, run_n_collect

def gen():
    return random.randint(0, 10)

def add(a: int, b: int) -> int:
    return a + b

def test_add():
    run = make_executor([gen, gen], add)
    results = run_n_collect(run, 5)
    assert len(results) == 5
    assert all(isinstance(r, int) for r in results)
```

Run it: `pytest state_testing/test_example.py -v` or `python -m state_testing` (if you keep the file in `state_testing/`).
