from argparse import ArgumentParser
from datetime import datetime, timedelta
from keyring import get_password, set_password
from getpass import getpass
import urllib3
import configparser

from py42.sdk import SDK
import py42.debug_level as debug_level
from py42 import settings
from c42secevents.extractors import AEDEventExtractor
from c42secevents.common import FileEventHandlers

from c42seceventcli.common.common import parse_timestamp, convert_date_to_timestamp
from c42seceventcli.aed.aed_cursor_store import AEDCursorStore
from c42seceventcli.common.cli_args import (
    add_authority_host_address_arg,
    add_username_arg,
    add_config_file_arg,
    add_begin_timestamp_arg,
    add_help_arg,
    add_ignore_ssl_errors_arg,
    add_output_format_arg,
    add_end_timestamp_arg,
    add_record_cursor_arg,
    add_event_type_args,
    add_debug_arg
)

_SERVICE = u"c42seceventcli"


def main():
    parser = _get_arg_parser()
    args = parser.parse_args()

    if args.c42_ignore_ssl_errors:
        _ignore_ssl_errors()

    if args.c42_debug_mode:
        settings.debug_level = debug_level.DEBUG

    if args.c42_config_file is None:
        username = args.c42_username
        host_address = args.c42_authority_url
    else:
        username = ""
        host_address = ""

    if host_address is None:
        print("Host address not provided.")
        parser.print_usage()
        exit(1)

    if username is None:
        print("Username not provided.")
        parser.print_usage()
        exit(1)

    password = _get_password(username)

    min_timestamp = parse_timestamp(args.c42_begin_date)
    max_timestamp = parse_timestamp(args.c42_end_date)

    if not _verify_min_timestamp(min_timestamp):
        print("Argument --begin must be within 90 days")
        exit(1)

    sdk = _create_sdk(address=host_address, username=username, password=password)
    handlers = _create_handlers(args.c42_output_format)
    extractor = AEDEventExtractor(sdk, handlers)
    extractor.extract(min_timestamp, max_timestamp, args.c42_event_types)


def _get_arg_parser():
    parser = ArgumentParser(add_help=False)
    logon_group = parser.add_mutually_exclusive_group(required=True)
    add_authority_host_address_arg(logon_group)
    add_config_file_arg(logon_group)

    # Makes sure that you can't give both an end_timestamp and tell it to record cursor positions
    mutually_exclusive_timestamp_group = parser.add_mutually_exclusive_group()
    add_end_timestamp_arg(mutually_exclusive_timestamp_group)
    add_record_cursor_arg(mutually_exclusive_timestamp_group)

    optionals = parser.add_argument_group("optional arguments")
    add_username_arg(optionals)
    add_help_arg(optionals)
    add_begin_timestamp_arg(optionals)
    add_ignore_ssl_errors_arg(optionals)
    add_output_format_arg(optionals)
    add_event_type_args(optionals)
    add_debug_arg(optionals)
    return parser


def _ignore_ssl_errors():
    settings.verify_ssl_certs = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get_password(username):
    password = get_password(_SERVICE, username)
    if password is None:
        pwd = getpass()
        set_password(_SERVICE, username, pwd)

    return password


def _verify_min_timestamp(min_timestamp):
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_date_to_timestamp(boundary_date)
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
