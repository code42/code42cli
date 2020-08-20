import click

from code42cli.logger import get_logger_for_server
from code42cli.output_formats import get_dynamic_header


def _process_events(output_format, events, output_header, include_all=False):
    if include_all:
        output_header = get_dynamic_header(events[0])

    def paginate():
        yield output_format(events, output_header)

    return paginate


def print_events(output_format, include_all, output_header):
    """Prints events to stdout"""

    def decorator(events):
        paginate = _process_events(output_format, events, output_header, include_all)
        if len(events) > 10:
            click.echo_via_pager(paginate)
        else:
            for page in paginate():
                click.echo(page)

    return decorator


def send_events(output_format, hostname, protocol, output_header, format_function):
    """Sends events to server/hostname"""

    def decorator(events):
        paginate = _process_events(format_function, events, output_header)

        logger = get_logger_for_server(hostname, protocol, output_format)
        for page in paginate():
            logger.handlers[0].emit(page)

    return decorator
