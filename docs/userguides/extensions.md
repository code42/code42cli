# Write custom extension scripts using the code42cli and py42

While the Code42 CLI aims to provide an easy way to automate many common Code42 tasks, there will likely be times when you need to script something the CLI doesn't have out-of-the-box.

To accommodate for those scenarios, the Code42 CLI exposes a few helper objects in the `code42cli.extensions` module that make it easy to write custom scripts with `py42` that use features of the CLI (like profiles) to reduce the amount of boilerplate needed to be productive. 

## Before you begin

The Code42 CLI is a python application written using the [click framework](https://click.palletsprojects.com/en/7.x/), and the exposed extension objects are custom `click` classes. A basic knowledge of how to define `click` commands, arguments, and options is required.

### The `sdk_options` decorator

The most important extension object is the `sdk_options` decorator. When you decorate a command you've defined in your script with `@sdk_options`, it will automatically add `--profile` and `--debug` options to your command. These work the same as in the main CLI commands. 

Decorating a command with `@sdk_options` also causes the first argument to your command function to be the `state` object, which contains the initialized py42 sdk. There's no need to handle user credentials or login, the `sdk_options` does all that for you using the CLI profiles.

### The `script` group

The `script` object exposed in the extensions module is a `click.Group` subclass, which allows you to add multiple sub-commands and group functionality together. While not explicitly required when writing custom scripts, the `script` group has logic to help handle and log any uncaught exceptions to the `~/.code42cli/log/code42_errors.log` file.

If only a single command is added to the `script` group, the group will default to that command, so you don't need to explicitly provide the sub-command name.

An example command that just prints the username and ID that the sdk is authenticated with:

```python
import click
from code42cli.extensions import script, sdk_options

@click.command()
@sdk_options
def my_command(state):
    user = state.sdk.users.get_current()
    print(user["username"], user["userId"])

if __name__ == "__main__":
    script.add_command(my_command)
    script()
```

## Ensuring your script runs in the Code42 CLI python environment

The above example works as a standalone script, if it were named `my_script.py` you could execute it by running:

```bash
python3 my_script.py
```

However, if the Code42 CLI is installed in a different python environment than your `python3` command it might fail to import the extensions.

To workaround environment and path issues, the CLI has a `--python` option that prints out the path to the python executable the CLI uses, so you can execute your script with `$(code42 --python) script.py` on Mac/Linux or `&$(code42 --python) script.py` on Windows to ensure it always uses the correct python path for the extension script to work. 

## Installing your extension script as a Code42 CLI plugin

The above example works as a standalone script, but it's also possible to install that same script as a plugin into the main CLI itself. 

Assuming the above example code is in a file called `my_script.py`, just add a file `setup.py` in the same directory with the following:

```python
from distutils.core import setup

setup(
    name="my_script",
    version="0.1",
    py_modules=["my_script"],
    install_requires=["code42cli"],
    entry_points="""
        [code42cli.plugins]
        my_command=my_script:my_command
    """,
)
```

The `entry_points` section tells the Code42 CLI where to look for the commands to add to its main group. If you have multiple commands defined in your script
you can add one per line in the `entry_points` and they'll all get installed into the Code42 CLI. 

Once your `setup.py` is ready, install it with pip while in the directory of `setup.py`: 

```
$(code42 --python) -m pip install .
```

Then running `code42 -h` should show `my-command` as one of the available commands to run!
