from argparse import ArgumentParser
from datetime import datetime, timedelta
from keyring import get_password, set_password
from getpass import getpass
import urllib3

from py42.sdk import SDK
from py42 import settings
from c42secevents.extractors import AEDEventExtractor
from c42secevents.common import FileEventHandlers

from c42seceventcli.common.common import parse_timestamp
from c42seceventcli.aed.aed_cursor_store import AEDCursorStore
from c42seceventcli.common.cli_args import (
    init_required_args,
    init_optional_arg_group,
    add_username_arg,
    add_begin_timestamp_arg,
    add_help_arg,
    add_ignore_ssl_errors_arg,
    add_output_format_arg,
    add_end_timestamp_arg,
    add_record_cursor_arg,
    add_event_type_args
)

_SERVICE = u"c42seceventcli"
_CREATED = u"CREATED"
_MODIFIED = u"MODIFIED"
_DELETED = u"DELETED"
_READ_BY_APP = u"READ_BY_APP"


def main():
    parser = _get_arg_parser()
    args = parser.parse_args()

    if args.c42_ignore_ssl_errors:
        _ignore_ssl_errors()

    username = args.c42_username
    password = _get_password(username)

    min_timestamp = parse_timestamp(args.c42_begin_date)
    max_timestamp = parse_timestamp(args.c42_end_date)

    if not _verify_min_timestamp(min_timestamp):
        print("Argument --begin must be within 90 days")
        exit(1)

    sdk = _create_sdk(address=args.c42_authority_url, username=username, password=password)
    handlers = _create_handlers(args.c42_output_format)
    extractor = AEDEventExtractor(sdk, handlers)
    extractor.extract(min_timestamp, max_timestamp, args.c42_event_types)


def _get_arg_parser():
    parser = ArgumentParser(add_help=False)

    required = init_required_args(parser)
    add_username_arg(required)

    # Makes sure that you can't give both an end_timestamp and tell it to record cursor positions
    mutually_exclusives = parser.add_mutually_exclusive_group()
    add_end_timestamp_arg(mutually_exclusives)
    add_record_cursor_arg(mutually_exclusives)

    optionals = init_optional_arg_group(parser)
    add_help_arg(optionals)
    add_begin_timestamp_arg(optionals)
    add_ignore_ssl_errors_arg(optionals)
    add_output_format_arg(optionals)
    add_event_type_args(optionals)
    return parser


def _ignore_ssl_errors():
    settings.verify_ssl_certs = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get_password(username):
    password = get_password(_SERVICE, username)
    if password is None:
        password = getpass()
        set_password(_SERVICE, username, password)

    return password


def _verify_min_timestamp(min_timestamp):
    now = datetime.utcnow()
    boundary = datetime.timestamp(now - timedelta(days=90))
    return min_timestamp >= boundary


def _create_sdk(address, username, password):
    return SDK.create_using_local_account(
        host_address=address, username=username, password=password
    )


def _create_handlers(output_type):
    store = AEDCursorStore()
    handlers = FileEventHandlers()

    handlers.record_cursor_position = store.replace_stored_insertion_timestamp
    handlers.get_cursor_position = store.get_stored_insertion_timestamp
    handlers.handle_response = _get_response_handler(output_type)
    return handlers


def _get_response_handler(output_format):
    def handle_response(response):
        print(response.text)
        # TODO: Replace with logging

    return handle_response


if __name__ == "__main__":
    main()
