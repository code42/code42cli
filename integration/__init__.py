import subprocess
import shlex


def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    response = ""
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        else:
            response += output.decode('utf-8')
    rc = process.poll()
    return rc, response


__all__ = [run_command]
