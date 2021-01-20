import os

import pexpect


LINE_FEED = b"\r\n"
PASSWORD_PROMPT = b"Password: "
ENCODING_TYPE = "utf-8"


def encode_response(line, encoding_type=ENCODING_TYPE):
    return line.decode(encoding_type)


def run_command(command):
    process = pexpect.spawn(command)
    response = []
    try:
        expected = process.expect([PASSWORD_PROMPT, pexpect.EOF])
        if expected == 0:
            process.sendline(os.environ["C42_PW"])
            process.expect(LINE_FEED)
            output = process.readlines()
            response = [encode_response(line) for line in output]
        else:
            output = process.before
            response = encode_response(output).splitlines()
    except pexpect.TIMEOUT:
        process.close()
        return process.exitstatus, response
    process.close()
    return process.exitstatus, response


__all__ = [run_command]
