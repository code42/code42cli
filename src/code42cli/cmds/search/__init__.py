from code42cli.errors import Code42CLIError
from code42cli.logger import get_logger_for_server


def try_get_logger_for_server(hostname, protocol, output_format, certs):
    try:
        return get_logger_for_server(hostname, protocol, output_format, certs)
    except Exception as err:
        raise Code42CLIError(
            "Unable to connect to {}. Failed with error: {}.".format(hostname, str(err))
        )
