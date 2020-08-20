import click

from code42cli.logger import get_logger_for_server


def print_events(format_function, output_header):
    """Prints events to stdout"""

    def decorator(events):

        result = format_function(events, output_header)
        if len(events) > 10:
            click.echo_via_pager(result)
        else:
            click.echo(result)

    return decorator


def send_events(output_format, hostname, protocol, output_header, format_function):
    """Sends events to server/hostname"""

    def decorator(events):
        logger = get_logger_for_server(hostname, protocol, output_format)
        result = format_function(events, output_header)
        logger.handlers[0].emit(result)

    return decorator
