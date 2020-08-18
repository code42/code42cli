import click
from c42eventextractor.logging.handlers import NoPrioritySysLogHandlerWrapper

from code42cli.output_formats import get_dynamic_header
from code42cli.util import get_url_parts


def _process_events(output_format, events, output_header, include_all=False):
    if include_all:
        output_header = get_dynamic_header(events[0])

    def paginate():
        yield output_format(events, output_header)

    return paginate


def print_events(events):
    """Prints events to stdout"""

    def decorator(output_format, include_all, output_header):
        paginate = _process_events(output_format, events, output_header, include_all)
        if len(events) > 10:
            click.echo_via_pager(paginate)
        else:
            for page in paginate():
                click.echo(page)

    return decorator


def send_events(events):
    """Sends events to server/hostname"""

    def decorator(output_format, hostname, protocol, output_header):
        paginate = _process_events(output_format, events, output_header)

        url_parts = get_url_parts(hostname)
        port = url_parts[1] or 514
        try:
            handler = NoPrioritySysLogHandlerWrapper(
                url_parts[0], port=port, protocol=protocol
            ).handler
        except Exception as e:
            raise Exception(
                "Unable to connect to {}. Error: {}".format(hostname, str(e))
            )
        for page in paginate():
            handler.emit(page)

    return decorator
