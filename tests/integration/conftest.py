import os
from shlex import split as split_command

import pytest
from tests.integration.util import DataServer

from code42cli.errors import Code42CLIError
from code42cli.main import cli
from code42cli.profile import get_profile


TEST_PROFILE_NAME = "TEMP-INTEGRATION-TEST"
_LINE_FEED = b"\r\n"
_PASSWORD_PROMPT = b"Password: "
_ENCODING_TYPE = "utf-8"


@pytest.fixture(scope="session")
def integration_test_profile(runner):
    """Creates a temporary profile to use for executing integration tests."""
    host = os.environ.get("C42_HOST") or "http://127.0.0.1:4200"
    username = os.environ.get("C42_USER") or "test_username@example.com"
    password = os.environ.get("C42_PW") or "test_password"
    delete_test_profile = split_command(f"profile delete {TEST_PROFILE_NAME} -y")
    create_test_profile = split_command(
        f"profile create -n {TEST_PROFILE_NAME} -u {username} -s {host} --password {password} -y"
    )
    runner.invoke(cli, delete_test_profile)
    result = runner.invoke(cli, create_test_profile)
    if result.exit_code != 0:
        pytest.exit(result.output)
    yield
    runner.invoke(cli, delete_test_profile)


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


@pytest.fixture(scope="session")
def tcp_dataserver():
    with DataServer(protocol="TCP"):
        yield


@pytest.fixture(scope="session")
def udp_dataserver():
    with DataServer(protocol="UDP"):
        yield
