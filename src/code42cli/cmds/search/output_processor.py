import click


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
