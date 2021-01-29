import os
from shlex import split as split_command

import pytest

from code42cli.errors import Code42CLIError
from code42cli.main import cli
from code42cli.options import CLIState
from code42cli.profile import get_profile


TEST_PROFILE_NAME = "TEMP-INTEGRATION-TEST"
_LINE_FEED = b"\r\n"
_PASSWORD_PROMPT = b"Password: "
_ENCODING_TYPE = "utf-8"


@pytest.fixture(scope="session")
def integration_test_profile(runner,):
    """Creates a temporary profile to use for executing integration tests."""
    host = os.environ.get("C42_HOST") or "http://127.0.0.1:4200"
    username = os.environ.get("C42_USER") or "test_username@example.com"
    password = os.environ.get("C42_PW") or "test_password"
    create_profile_command = "profile create -n {} -u {} -s {} --password {} -y"
    runner.invoke(
        cli,
        split_command(
            create_profile_command.format(TEST_PROFILE_NAME, username, host, password)
        ),
    )
    runner.invoke(cli, split_command("profile use {}".format(TEST_PROFILE_NAME)))
    state = CLIState()
    yield state
    runner.invoke(cli, "profile delete {} -y".format(TEST_PROFILE_NAME))


def _get_current_profile_name():
    try:
        profile = get_profile()
        return profile.name
    except Code42CLIError:
        return None


def _encode_response(line, encoding_type=_ENCODING_TYPE):
    return line.decode(encoding_type)


def append_profile(command):
    return "{} --profile {}".format(command, TEST_PROFILE_NAME)
