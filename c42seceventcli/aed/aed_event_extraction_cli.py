from argparse import ArgumentParser
import urllib3

from py42.sdk import SDK
from py42 import settings
from c42secevents.extractors import extract_aed_events
from c42secevents.common import FileEventHandlers

from c42seceventcli.aed.aed_cursor_store import AEDCursorStore
from c42seceventcli.common.cli_args import (
    get_required_credential_args,
    add_begin_timestamp_arg,
    add_help_arg,
    add_ignore_ssl_errors_arg,
)


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
    get_required_credential_args(parser)
    optional = parser.add_argument_group("optional arguments")
    add_help_arg(optional)
    add_begin_timestamp_arg(optional)
    add_ignore_ssl_errors_arg(optional)
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
