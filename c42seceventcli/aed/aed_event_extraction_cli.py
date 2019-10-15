from argparse import ArgumentParser
from datetime import datetime, timedelta
from keyring import get_password, set_password
from getpass import getpass
import urllib3

from py42.sdk import SDK
import py42.debug_level as debug_level
from py42 import settings
from c42secevents.extractors import AEDEventExtractor
from c42secevents.common import FileEventHandlers

from c42seceventcli.common.common import SecEventConfigParser, parse_timestamp, convert_date_to_timestamp
from c42seceventcli.aed.aed_cursor_store import AEDCursorStore
from c42seceventcli.common.cli_args import (
    add_authority_host_address_arg,
    add_username_arg,
    add_begin_date_arg,
    add_end_date_arg,
    add_ignore_ssl_errors_arg,
    add_output_format_arg,
    add_record_cursor_arg,
    add_exposure_types_arg,
    add_debug_arg,
    add_help_arg,
)

_SERVICE_NAME_FOR_KEYCHAIN = u"c42seceventcli"


def main():
    parser = _get_arg_parser()
    cli_args = parser.parse_args()
    config = _get_config()
    args = _get_args(cli_args, config)

    if args.get("ignore_ssl_errors"):
        _ignore_ssl_errors()

    if args.get("debug_mode"):
        settings.debug_level = debug_level.DEBUG

    server = args.get("server")
    username = args.get("username")

    if server is None:
        _exit_from_argument_error("Host address not provided.", parser)

    if username is None:
        _exit_from_argument_error("Username not provided.", parser)

    password = _get_password(username)
    min_timestamp = parse_timestamp(args.get("begin_date"))
    max_timestamp = parse_timestamp(args.get("end_date"))

    if not _verify_min_timestamp(min_timestamp):
        print("Argument --begin must be within 90 days")
        exit(1)

    sdk = SDK.create_using_local_account(host_address=server, username=username, password=password)
    handlers = _create_handlers(args.get("output_format"))
    extractor = AEDEventExtractor(sdk, handlers)
    extractor.extract(min_timestamp, max_timestamp, args.get("exposure_types"))


def _get_arg_parser():
    parser = ArgumentParser(add_help=False)

    # Makes sure that you can't give both an end_timestamp and record cursor positions
    mutually_exclusive_timestamp_group = parser.add_mutually_exclusive_group()
    add_end_date_arg(mutually_exclusive_timestamp_group)
    add_record_cursor_arg(mutually_exclusive_timestamp_group)

    main_args = parser.add_argument_group("main")
    add_authority_host_address_arg(main_args)
    add_username_arg(main_args)
    add_help_arg(main_args)
    add_begin_date_arg(main_args)
    add_ignore_ssl_errors_arg(main_args)
    add_output_format_arg(main_args)
    add_exposure_types_arg(main_args)
    add_debug_arg(main_args)
    return parser


def _get_config():
    config = SecEventConfigParser("config.cfg")
    return config if config.is_valid else None


def _get_args(cli_args, config_parser):
    args = {
        "username": cli_args.c42_username
        if cli_args.c42_username
        else config_parser.parse_username(),
        "server": cli_args.c42_authority_url
        if cli_args.c42_authority_url
        else config_parser.parse_server(),
        "begin_date": cli_args.c42_begin_date
        if cli_args.c42_begin_date
        else config_parser.parse_begin_date(),
        "end_date": cli_args.c42_end_date
        if cli_args.c42_end_date
        else config_parser.parse_end_date(),
        "ignore_ssl_errors": cli_args.c42_ignore_ssl_errors
        if cli_args.c42_ignore_ssl_errors
        else config_parser.parse_ignore_ssl_errors(),
        "output_format": cli_args.c42_output_format
        if cli_args.c42_output_format
        else config_parser.parse_output_format(),
        "record_cursor": cli_args.c42_record_cursor
        if cli_args.c42_record_cursor
        else config_parser.parse_record_cursor(),
        "exposure_types": cli_args.c42_exposure_types
        if cli_args.c42_exposure_types
        else config_parser.parse_exposure_types(),
        "debug_mode": cli_args.c42_debug_mode
        if cli_args.c42_debug_mode
        else config_parser.parse_debug_mode(),
    }
    return args


def _ignore_ssl_errors():
    settings.verify_ssl_certs = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get_password(username):
    password = get_password(_SERVICE_NAME_FOR_KEYCHAIN, username)
    if password is None:
        pwd = getpass()
        set_password(_SERVICE_NAME_FOR_KEYCHAIN, username, pwd)

    return password


def _verify_min_timestamp(min_timestamp):
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_date_to_timestamp(boundary_date)
    return min_timestamp >= boundary


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
        # TODO: Replace with logging from Alan's branch

    return handle_response


def _exit_from_argument_error(message, parser):
    print(message)
    parser.print_usage()
    exit(1)


if __name__ == "__main__":
    main()
