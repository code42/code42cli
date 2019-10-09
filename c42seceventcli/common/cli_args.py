from argparse import SUPPRESS


def get_required_credential_args(parser):
    required = parser.add_argument_group("required arguments")
    add_authority_host_address_arg(required)
    add_username_arg(required)
    add_password_arg(required)
    return required


def add_authority_host_address_arg(arg_group):
    arg_group.add_argument(
        "-s",
        "--server",
        dest="c42_authority_url",
        action="store",
        help="The full scheme, url and port of the Code42 server.",
        required=True,
    )


def add_username_arg(arg_group):
    arg_group.add_argument(
        "-u",
        "--username",
        action="store",
        dest="c42_username",
        help="The username of the Code42 API user.",
        required=True,
    )


def add_password_arg(arg_group):
    arg_group.add_argument(
        "-p",
        "--password",
        action="store",
        dest="c42_password",
        help="The password of the Code42 API user.",
        required=True,
    )


def add_help_arg(arg_group):
    arg_group.add_argument(
        "-h", "--help", action="help", default=SUPPRESS, help="Show this help message and exit"
    )


def add_begin_timestamp_arg(arg_group):
    arg_group.add_argument(
        "-b",
        "--begin",
        action="store",
        dest="c42_begin_date",
        help="The beginning of the date range in which to look for events, "
        "in YYYY-MM-DD format OR a number (number of minutes ago).",
    )


def add_ignore_ssl_errors_arg(arg_group):
    arg_group.add_argument(
        "-i",
        "--ignore-ssl-errors",
        action="store_true",
        dest="c42_ignore_ssl_errors",
        help="Set to ignore ssl errors.",
    )
