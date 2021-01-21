import os
import time

from tests.integration import run_command


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


START_DOCKER_DAEMON_COMMAND = "open --background -a Docker"
DOCKER_INFO_COMMAND = "docker info"
GET_DOCKER_PROCESS_NAME_COMMAND = (
    '/bin/bash -c "launchctl list | grep docker | cut -f3 | grep -v helper"'
)
STOP_DOCKER_DAEMON_COMMAND = "launchctl stop {}"


class DockerDaemon:
    def __init__(self):
        self.process_name = None

    def __enter__(self):
        # Need to change to Unix
        if not self._check_docker_state():
            exit_status, _ = run_command(START_DOCKER_DAEMON_COMMAND)
            if exit_status == 0:
                self._wait_for_docker_daemon_to_be_up()
            else:
                raise Exception("Failed to start docker daemon.")
        self._set_docker_process_name()

    def _check_docker_state(self):
        exit_status, _ = run_command(DOCKER_INFO_COMMAND)
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
        exit_status, response = run_command(GET_DOCKER_PROCESS_NAME_COMMAND)
        if exit_status == 0:
            self.process_name = response[0]
        else:
            raise Exception("Could not find docker daemon.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Need to change to Unix
        if self.process_name is not None:
            exit_status, response = run_command(
                STOP_DOCKER_DAEMON_COMMAND.format(self.process_name)
            )
            if exit_status != 0:
                print("Failed to stop the docker daemon, error {}".format(response))


class SyslogServer:

    PATH_ENV = "COMPOSE_FILE"

    def __enter__(self):
        if not os.environ[SyslogServer.PATH_ENV]:
            raise Exception(
                "Set environment variable: {}".format(SyslogServer.PATH_ENV)
            )
        exit_status, response = run_command("docker-compose up")
        if exit_status != 0:
            raise Exception("Could not start syslog server.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        exit_status, response = run_command("docker-compose down")
        if exit_status != 0:
            print("Failed to stop syslog server.")
