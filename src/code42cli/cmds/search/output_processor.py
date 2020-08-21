import click

from code42cli.logger import get_logger_for_server


def print_events(format_function, output_header):
    """Prints events to stdout"""

    def decorator(events):
        def paginate():
            yield format_function(events, output_header)

        if len(events) > 10:
            click.echo_via_pager(paginate)
        else:
            for page in paginate():
                click.echo(page)

    return decorator


def send_events(output_format, hostname, protocol, output_header, format_function):
    """Sends events to server/hostname"""

    def decorator(events):
        logger = get_logger_for_server(hostname, protocol, output_format)

        for event in events:
            logger.handlers[0].emit(format_function(event, output_header))

    return decorator
