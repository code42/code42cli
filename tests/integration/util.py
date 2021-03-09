import os
import subprocess
import time
from shlex import split as split_command

from code42cli.main import cli


class cleanup:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        return open(self.filename)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.filename)


def cleanup_after_validation(filename):
    """Decorator to read response from file for `write-to` commands and cleanup the file after test
    execution.

    The decorated function should return validation function that takes the content of the file
    as input. e.g
    """

    def wrap(test_function):
        def wrapper():
            validate = test_function()
            with cleanup(filename) as f:
                response = f.read()
                validate(response)

        return wrapper

    return wrap


class DataServer:
    TCP_SERVER_COMMAND = "ncat -l 5140"
    UDP_SERVER_COMMAND = "ncat -ul 5141"

    def __init__(self, protocol="TCP"):
        if protocol.upper() == "UDP":
            self.command = DataServer.UDP_SERVER_COMMAND
        else:
            self.command = DataServer.TCP_SERVER_COMMAND
        self.process = None

    def __enter__(self):
        self.process = subprocess.Popen(self.command, shell=True)
        time.sleep(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process.kill()


def assert_test_is_successful(runner, command):
    result = runner.invoke(cli, split_command(command))
    assert result.exit_code == 0
