from argparse import SUPPRESS


def add_clear_cursor_arg(arg_group):
    arg_group.add_argument(
        "--clear-cursor",
        dest="clear_cursor",
        action="store_true",
        help="Resets the stored cursor.",
        default=False,
    )


def add_begin_date_arg(arg_group):
    arg_group.add_argument(
        "-b",
        "--begin",
        action="store",
        dest="begin_date",
        help="The beginning of the date range in which to look for events, "
        "in YYYY-MM-DD UTC format OR a number (number of minutes ago).",
    )


def add_end_date_arg(arg_group):
    arg_group.add_argument(
        "-e",
        "--end",
        action="store",
        dest="end_date",
        help="The end of the date range in which to look for events, "
        "in YYYY-MM-DD UTC format OR a number (number of minutes ago).",
    )


def add_ignore_ssl_errors_arg(arg_group):
    arg_group.add_argument(
        "-i",
        "--ignore-ssl-errors",
        action="store_true",
        dest="ignore_ssl_errors",
        help="Do not validate the SSL certificates of Code42 servers.",
    )


def add_output_format_arg(arg_group):
    arg_group.add_argument(
        "-o",
        "--output-format",
        dest="output_format",
        action="store",
        choices=["CEF", "JSON"],
        help="The format used for outputting events.",
    )


def add_record_cursor_arg(arg_group):
    arg_group.add_argument(
        "-r",
        "--record-cursor",
        dest="record_cursor",
        action="store_true",
        help="Only get events that were not previously retrieved.",
    )


def add_exposure_types_arg(arg_group):
    arg_group.add_argument(
        "-t",
        "--types",
        nargs="*",
        action="store",
        dest="exposure_types",
        choices=[
            u"SharedViaLink",
            u"SharedToDomain",
            u"ApplicationRead",
            u"CloudStorage",
            u"RemovableMedia",
            u"IsPublic",
        ],
        help="To limit extracted events to those with given exposure types.",
    )


def add_debug_arg(arg_group):
    arg_group.add_argument(
        "-d" "--debug", action="store_true", dest="debug_mode", help="Turn on debug logging."
    )


def add_destination_type_arg(arg_group):
    arg_group.add_argument(
        "--dest-type",
        action="store",
        dest="destination_type",
        choices=["stdout", "file", "server"],
        help="The type of destination to send output to.",
    )


def add_destination_arg(arg_group):
    arg_group.add_argument(
        "--dest",
        action="store",
        dest="destination",
        help="Either a name of a local file or syslog host address. Ignored if destination type is 'stdout'.",
    )


def add_destination_port_arg(arg_group):
    arg_group.add_argument(
        "--dest-port",
        action="store",
        dest="destination_port",
        help="Port used when sending logs to server. Ignored if destination type is not 'server'.",
    )


def add_destination_protocol_arg(arg_group):
    arg_group.add_argument(
        "--dest-protocol",
        action="store",
        dest="destination_protocol",
        choices=["TCP", "UDP"],
        help="Protocol used to send logs to server. Ignored if destination type is not 'server'.",
    )


def add_help_arg(arg_group):
    arg_group.add_argument(
        "-h", "--help", action="help", default=SUPPRESS, help="Show this help message and exit."
    )
