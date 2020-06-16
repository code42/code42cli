import os
import pexpect


LINE_FEED = b'\r\n'
PASSWORD_PROMPT = b'Password: '


def command_response(lines):
    return [line.decode('utf-8') for line in lines]


def run_command(command):

    process = pexpect.spawn(command)
    response = ""
    try:
        expected = process.expect([PASSWORD_PROMPT, LINE_FEED])
        if expected == 0:
            process.sendline(os.environ["C42_PW"])
            process.expect(LINE_FEED)
        response = command_response(process.readlines())

    except pexpect.EOF:
        return 0, response
    except pexpect.TIMEOUT:
        return 1, response
    return 0, response


__all__ = [run_command]
