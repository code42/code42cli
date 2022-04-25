- [Set up your Development environment](#set-up-your-development-environment)
  - [macOS](#macos)
  - [Windows/Linux](#windowslinux)
- [Installation](#installation)
- [Run a full build](#run-a-full-build)
- [Coding Style](#coding-style)
  - [Style linter](#style-linter)
- [Tests](#tests)
  - [Writing tests](#writing-tests)
- [Documentation](#documentation)
  - [Generating documentation](#generating-documentation)
    - [Performing a test build](#performing-a-test-build)
    - [Running the docs locally](#running-the-docs-locally)
- [Changes](#changes)
- [Opening a PR](#opening-a-pr)

## Set up your Development environment

The very first thing to do is to fork the code42cli repo, clone it, and make it your working directory!

```bash
git clone https://github.com/myaccount/code42cli
cd code42cli
```

To set up your development environment, create a python virtual environment and activate it. This keeps your dependencies sandboxed so that they are unaffected by (and do not affect) other python packages you may have installed.

### macOS

There are many ways to do this (you can also use the method outlined for Windows/Linux below), but we recommend using [pyenv](https://github.com/pyenv/pyenv).

Install `pyenv` and `pyenv-virtualenv` via [homebrew](https://brew.sh/):

```bash
brew install pyenv pyenv-virtualenv
```

After installing `pyenv` and `pyenv-virtualenv`, be sure to add the following entries to your `.zshrc` (or `.bashrc` if you are using bash) and restart your shell:

```bash
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Then, create your virtual environment.

```bash
pyenv install 3.9.10
pyenv virtualenv 3.9.10 code42cli
pyenv activate code42cli
```

**Note**: The CLI supports pythons versions 3.6 through 3.9 for end users. However due to some of the build dependencies, you'll need a version >=3.7 for your virtual environment.  Use `pyenv --versions` to see all versions available for install. There are some known issues installing python 3.6 with pyenv on certain OS.

Use `source deactivate` to exit the virtual environment and `pyenv activate code42cli` to reactivate it.

### Windows/Linux

Install a version of python 3.6 or higher from [python.org](https://python.org).
Next, in a directory somewhere outside the project, create and activate your virtual environment:

```bash
python -m venv code42cli
# macOS/Linux
source code42cli/bin/activate
# Windows
.\code42cli\Scripts\Activate
```

To leave the virtual environment, simply use:
```bash
deactivate
```

## Installation

Next, with your virtual environment activated, install code42cli and its development dependencies. The `-e` option installs code42cli in
["editable mode"](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs).

```bash
pip install -e .'[dev]'
```

Open the project in your IDE of choice and change the python environment to
point to your virtual environment, and you should be ready to go!

## Run a full build

We use [tox](https://tox.readthedocs.io/en/latest/#) to run our build against Python 3.6, 3.7, and 3.8. When run locally, `tox` will run only against the version of python that your virtual envrionment is running, but all versions will be validated against when you [open a PR](#opening-a-pr).

To run all the unit tests, do a test build of the documentation, and check that the code meets all style requirements, simply run:

```bash
tox
```
If the full process runs without any errors, your environment is set up correctly! You can also use `tox` to run sub-parts of the build, as explained below.

## Coding Style

Use syntax and built-in modules that are compatible with Python 3.6+.

### Style linter

When you open a PR, after all of the unit tests successfully pass, a series
of style checks will run. See the [pre-commit-config.yaml](.pre-commit-config.yaml) file to see a list of the projects involved in this automation. If your code does not pass the style checks, the PR will not be allowed to merge. Many of the style rules can be corrected automatically by running a simple command once you are satisfied with your change:

```bash
tox -e style
```

This will output a diff of the files that were changed as well a list of files / line numbers / error descriptions for any style problems that need to be corrected manually. Once these have been corrected and re-pushed, the PR checks should pass.

You can optionally also choose to have these checks / automatic adjustments
occur automatically on each git commit that you make (instead of only when running `tox`.) To do so, install `pre-commit` and install the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Tests

This will also test that the documentation build passes and run the style checks. If you want to _only_ run the unit tests, you can use:

```bash
$ tox -e py
```

If you want to run the integration tests in your current python environment, you can do:

```bash
pytest -m "integration"
```

Integration tests have a dependency on `nmap` module to test `send-to` commands.

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

## Documentation

Command functions should have accompanying documentation. Documentation is written in markdown and managed in the `docs` folder of this repo.

### Generating documentation

code42cli uses [Sphinx](http://www.sphinx-doc.org/) to generate documentation.

#### Performing a test build

To simply test that the documentation build without errors, you can run:

```bash
tox -e docs
```

#### Running the docs locally

To build and run the documentation locally, run the following from the `docs` directory:

```bash
pip install sphinx myst-parser sphinx_rtd_theme
make html
```

To view the resulting documentation, open `docs/_build/html/index.html`.

For the best viewing experience, run a local server to view the documentation.
You can this by running the below from the `docs` directory using python 3:

```bash
python -m http.server --directory "_build/html" 1337
```

and then pointing your browser to `localhost:1337`.

## Changes

Document all notable consumer-affecting changes in CHANGELOG.md per principles and guidelines at
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Opening a PR

When you're satisfied with your changes, open a PR and fill out the pull request template file. We recommend prefixing the name of your branch and/or PR title with `bugfix`, `chore`, or `feature` to help quickly categorize your change. Your unit tests and other checks will run against all supported python versions when you do this.

For contributions from non-Code42 employees, we require you to agree to our [Contributor License Agreement](https://code42.github.io/code42-cla/Code42_Individual_Contributor_License_Agreement).

On submission of your first PR, a GitHub action will run requiring you to reply in a comment with your affirmation of the CLA before the PR will be able to be merged.

A team member should get in contact with you shortly to help merge your PR to completion and get it ready for a release!
