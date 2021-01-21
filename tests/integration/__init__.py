import os
from contextlib import contextmanager
import pexpect

from code42cli.errors import Code42CLIError
from code42cli.profile import create_profile
from code42cli.profile import switch_default_profile
from code42cli.profile import get_profile
from code42cli.profile import delete_profile

TEST_PROFILE_NAME = "TEMP-INTEGRATION-TEST"
_LINE_FEED = b"\r\n"
_PASSWORD_PROMPT = b"Password: "
_ENCODING_TYPE = "utf-8"


@contextmanager
def use_temp_profile():
    """Creates a temporary profile to use for executing integration tests."""
    host = os.environ.get("C42_HOST") or "http://127.0.0.1:4200"
    username = os.environ.get("C42_USER") or "test_username@example.com"
    password = os.environ.get("C42_PW") or "test_password"
    current_profile_name = _get_current_profile_name()
    create_profile(TEST_PROFILE_NAME, host, username, True)
    switch_default_profile(TEST_PROFILE_NAME)
    yield password
    delete_profile(TEST_PROFILE_NAME)
    
    # Switch back to the original profile if there was one
    if current_profile_name:
        switch_default_profile(current_profile_name)
    

def _get_current_profile_name():
    try:
        profile = get_profile()
        return profile.name
    except Code42CLIError:
        return None


def run_command(command):
    with use_temp_profile() as pw:
        process = pexpect.spawn(command)
        response = []
        try:
            expected = process.expect([_PASSWORD_PROMPT, pexpect.EOF])
            if expected == 0:
                process.sendline(pw)
                process.expect(_LINE_FEED)
                output = process.readlines()
                response = [_encode_response(line) for line in output]
            else:
                output = process.before
                response = _encode_response(output).splitlines()
        except pexpect.TIMEOUT:
            process.close()
            return process.exitstatus, response
        process.close()
        return process.exitstatus, response

def _encode_response(line, encoding_type=_ENCODING_TYPE):
    return line.decode(encoding_type)


__all__ = [run_command]
