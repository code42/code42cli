import os

import pexpect

from code42cli.profile import create_profile
from code42cli.profile import delete_profile

TEST_PROFILE_NAME = "TEMP-INTEGRATION-TEST"
_LINE_FEED = b"\r\n"
_PASSWORD_PROMPT = b"Password: "
_ENCODING_TYPE = "utf-8"


def run_command(command):
    command = _attach_profile_arg(command)
    with use_temp_profile() as temp_password:
        return _run_command_as_process(command, temp_password)


class use_temp_profile:
    """Creates a temporary profile to use for executing integration tests."""

    def __init__(self):
        self._host = os.environ.get("C42_HOST") or "http://127.0.0.1:4200"
        self._username = os.environ.get("C42_USER") or "test_username@example.com"
        self._password = os.environ.get("C42_PW") or "test_password"

    def __enter__(self):
        create_profile(TEST_PROFILE_NAME, self._host, self._username, True)
        return self._password

    def __exit__(self, exc_type, exc_val, exc_tb):
        delete_profile(TEST_PROFILE_NAME)
        return False


def _run_command_as_process(command, temp_password):
    process = None
    response = []
    try:
        process = pexpect.spawn(command, timeout=5)
        response = _get_response(process, temp_password)
        return process.exitstatus, response
    except Exception:
        if process:
            return process.exitstatus, response
    finally:
        if process:
            process.close()


def _attach_profile_arg(command):
    return "{} --profile {}".format(command, TEST_PROFILE_NAME)


def _get_response(process, password):
    expected = process.expect([_PASSWORD_PROMPT, pexpect.EOF])
    if expected == 0:
        _set_password(process, password)
        return _get_response_from_multiline_output(process)
    else:
        output = process.before
        return _encode_response(output).splitlines()


def _set_password(process, password):
    process.sendline(password)
    process.expect(_LINE_FEED)


def _get_response_from_multiline_output(process):
    output = process.readlines()
    return [_encode_response(line) for line in output]


def _encode_response(line, encoding_type=_ENCODING_TYPE):
    return line.decode(encoding_type)


__all__ = [run_command]
