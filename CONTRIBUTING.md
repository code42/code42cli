# Contributing to code42cli

## Development environment

Install code42cli and its development dependencies. The `-e` option installs py42 in 
["editable mode"](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs). 

```bash
$ pip install -e .[dev]
```

If you are using `zsh`, you may need to escape the brackets.

We use [black](https://black.readthedocs.io/en/stable/) to automatically format our code.
After installing dependencies, be sure to run:

```bash
$ pre-commit install
```

This will set up a pre-commit hook that will automatically format your code to our desired styles whenever you commit.
It requires python 3.6 to run, so be sure to have a python 3.6 executable of some kind in your PATH when you commit.

## General

* Use positional argument specifiers in `str.format()`
* Use syntax and built-in modules that are compatible with both Python 2 and 3.
* Use the `code42cli._internal.compat` module to create abstractions around functionality that differs between 2 and 3.

## Changes

Document all notable consumer-affecting changes in CHANGELOG.md per principles and guidelines at 
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Tests

We use [tox](https://tox.readthedocs.io/en/latest/#) to run the 
[pytest](https://docs.pytest.org/) test framework on Python 2.7, 3.5, 3.6, and 3.7.

To run all tests, run this at the root of the repo:

```bash
$ tox
```

If you're using a virtual environment, this will only run the tests within that environment/version of Python.
To run the tests on all supported versions of Python in a local dev environment, we recommend using 
[pyenv](https://github.com/pyenv/pyenv) and tox in your system (non-virtual) environment:

```bash
$ pip install tox
$ pyenv install 2.7.16
$ pyenv install 3.5.7
$ pyenv install 3.6.9
$ pyenv install 3.7.4
$ pyenv local 2.7.16 3.5.7 3.6.9 3.7.4
$ tox
```

### Writing tests

Put actual before expected values in assert statements. Pytest assumes this order.

```python
a = 4
assert a % 2 == 0
```

Use the following naming convention with test methods:  

test\_\[unit_under_test\]\_\[variables_for_the_test\]\_\[expected_state\]

Example:

```python
def test_add_one_and_one_equals_two():
```
