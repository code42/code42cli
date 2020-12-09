import os
import time

from integration import run_command


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


class DockerDaemon:
    def __init__(self):
        self.process_name = None

    def __enter__(self):
        # Need to change to Unix
        if not self._check_docker_state():
            mac_command = "open --background -a Docker"
            exit_status, _ = run_command(mac_command)
            if exit_status == 0:
                self._wait_for_docker_daemon_to_be_up()
            else:
                # Fail here, raise exception
                pass
        self._set_docker_process_name()

    def _check_docker_state(self):
        exit_status, _ = run_command("docker info")
        if exit_status == 0:
            return True
        return False

    def _wait_for_docker_daemon_to_be_up(self):
        while True:
            if self._check_docker_state():
                break
            time.sleep(10)

    def _set_docker_process_name(self):
        # Need to change to Unix
        mac_command = (
            '/bin/bash -c "launchctl list | grep docker | cut -f3 | grep -v helper"'
        )
        exit_status, response = run_command(mac_command)
        print(f"process name is {response[0]}")
        if exit_status == 0:
            self.process_name = response[0]

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Need to change to Unix
        if self.process_name is not None:
            stop_command = f"launchctl stop {self.process_name}"
            exit_status, response = run_command(stop_command)
            if (
                exit_status != 0
            ):  # being explicit here, if exit_status too should be ok.
                print(f"Failed to stop the docker daemon, error {response}")


class SyslogServer:
    def __enter__(self):
        # TODO change hard-coded path
        command = "/bin/bash -c 'docker ps | grep test-server_centossyslog_1'"
        exit_status, response = run_command(command)
        print(f"docker ps command response: {response}")
        if exit_status != 0:
            command = (
                "sh /Users/kchaudhary/workspace/test-server/start-syslog-server.sh"
            )
            exit_status, response = run_command(command)
            print(f"shell script response: {response}")
            if exit_status != 0:
                # Fail here, raise exception
                pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        command = "docker stop test-server_centossyslog_1"
        exit_status, response = run_command(command)
