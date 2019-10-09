from argparse import SUPPRESS
from argparse import ArgumentParser
import urllib3

from py42.sdk import SDK
from py42 import settings
from c42secevents.extractors import extract_aed_events
from c42secevents.common import FileEventHandlers
from c42seceventcli.aed.aed_cursor_store import AEDCursorStore


def main():
    parser = _get_arg_parser()
    args = parser.parse_args()

    if args.c42_ignore_ssl_errors:
        _ignore_ssl_errors()

    sdk = _create_sdk(
        address=args.c42_authority_url, username=args.c42_username, password=args.c42_password
    )

    _set_handlers()
    extract_aed_events(sdk)


def _get_arg_parser():
    parser = ArgumentParser(add_help=False)
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")
    required.add_argument(
        "-s",
        "--server",
        dest="c42_authority_url",
        action="store",
        help="The full scheme, url and port of the Code42 server.",
        required=True,
    )
    required.add_argument(
        "-u",
        "--username",
        action="store",
        dest="c42_username",
        help="The username of the Code42 API user.",
        required=True,
    )
    required.add_argument(
        "-p",
        "--password",
        action="store",
        dest="c42_password",
        help="The password of the Code42 API user.",
        required=True,
    )
    optional.add_argument(
        "-b",
        "--begin",
        action="store",
        dest="c42_begin_date",
        help="The beginning of the date range in which to look for events, "
        "in YYYY-MM-DD format OR a number (number of minutes ago).",
    )
    optional.add_argument(
        "-h", "--help", action="help", default=SUPPRESS, help="Show this help message and exit"
    )
    optional.add_argument(
        "-i",
        "--ignore-ssl-errors",
        action="store_true",
        dest="c42_ignore_ssl_errors",
        help="Set to ignore ssl errors.",
    )
    return parser


def _ignore_ssl_errors():
    settings.verify_ssl_certs = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _create_sdk(address, username, password):
    return SDK.create_using_local_account(
        host_address=address, username=username, password=password
    )


def _set_handlers():
    store = AEDCursorStore()

    def record_timestamp(timestamp):
        store.insertion_timestamp = timestamp

    def get_timestamp():
        return store.insertion_timestamp

    FileEventHandlers.record_cursor_position = record_timestamp
    FileEventHandlers.get_cursor_position = get_timestamp
    # TODO: FileEventHandlers.handle_response = HOOK FOR LOGGING


if __name__ == "__main__":
    main()
