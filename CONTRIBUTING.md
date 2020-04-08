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
It requires python 3.6+ to run, so be sure to have a qualifying python executable in your PATH when you commit.

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

### Adding a new command

See class documentation on the [Command](src/code42cli/commands.py) class for an explanation of its constructor parameters.

1. If you are creating a new top-level command, create a new instance of `Command` and add it to the list returned
    by `_load_top_commands()` function in `code42cli.main`.

2. If you are creating a new subcommand, find the top-level command that this will be a subcommand of in
    `_load_top_commands()` in `code42cli.main` and navigate to the function assigned to be its subcommand loader.
     Then, add a new instance of `Command` to the list returned by that function.

3. For commands that actually are executed (rather than just being groups), you will add a `handler` function as a constructor parameter.
   This will be the function that you want to execute when your command is run.
   * _Positional_ arguments of the handler will automatically become _required_ cli arguments
   * _Keyword_ arguments of the handler will automatically become _optional_ cli arguments
   * the cli argument name will be the same as the handler param name except with `_` replaced with `-`, and prefixed with `--` if optional

    For example, consider the following python function:

    ```python
    def handler_example(one, two, three=None, four=None):
        pass
    ```

    When the above function is supplied as a `Command`'s `handler` parameter, the result will be a command that can be executed as follows
    (assuming `cmd` is the name given to the command):

    ```bash
    $ code42 cmd oneval twoval --three threeval --four fourval
    ```

4. To add descriptions to your cli arguments to appear in the help text, your command takes a function as the `arg_customizer` parameter.
    The entire [`ArgConfigCollection`](src/code42cli/args.py) that was automatically created is supplied as the only argument to this function
    and can be modified by it. See `code42cli.cmds.profile._load_profile_create_descriptions` for an example of this.

5. If one of your handler's parameters is named `sdk`, you will automatically get a `--profile` argument available in the cli and the `sdk` parameter
    will automatically contain an instance of `py42.sdk.SDKClient` that was created with the given (or default) profile.
    - A cli parameter named `--sdk` will _not_ be added in this case.

6. If you have an `sdk` parameter, a parameter named `profile` will automatically contain the info of the profile that was used to create the sdk.
    - A parameter named `profile` behaves normally if you do not also have a parameter named `sdk`.


7. Each command accepts a `use_single_arg_obj` bool in its constructor. If set to true, this will instead cause the handler to be called with a single object
    containing all of the args as attributes, which will be passed to a variable named `args` in your handler. Since your handler will only contain the parameter `args`,
    the names of your cli parameters need to built manually in your `arg_customizer` if you use this option. An example of this can be seen in `code42cli.cmds.securitydata.main`.
