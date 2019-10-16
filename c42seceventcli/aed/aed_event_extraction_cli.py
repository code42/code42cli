import urllib3
import json
from argparse import ArgumentParser
from datetime import datetime, timedelta
from keyring import get_password, set_password
from getpass import getpass

import py42.debug_level as debug_level
from py42.sdk import SDK
from py42 import settings
from c42secevents.extractors import AEDEventExtractor
from c42secevents.common import FileEventHandlers, convert_datetime_to_timestamp
from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter

from c42seceventcli.common.common import SecurityEventConfigParser, parse_timestamp, get_logger
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
    add_destination_type_arg,
    add_destination_arg,
    add_syslog_port_arg,
    add_syslog_protocol_arg,
    add_help_arg,
)

_SERVICE_NAME_FOR_KEYCHAIN = u"c42seceventcli"


def main():
    parser = _get_arg_parser()
    cli_args = parser.parse_args()
    config_parser = SecurityEventConfigParser("config.cfg")
    args = _union_cli_args_with_config_args(cli_args, config_parser)

    if args.ignore_ssl_errors:
        _ignore_ssl_errors()

    if args.debug_mode:
        settings.debug_level = debug_level.DEBUG

    min_timestamp = _parse_min_timestamp(args)
    max_timestamp = parse_timestamp(args.end_date)

    sdk = _create_sdk_from_args(args, parser)
    handlers = _create_handlers(args)
    extractor = AEDEventExtractor(sdk, handlers)
    extractor.extract(min_timestamp, max_timestamp, args.exposure_types)


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
    add_destination_type_arg(main_args)
    add_destination_arg(main_args)
    add_syslog_port_arg(main_args)
    add_syslog_protocol_arg(main_args)
    return parser


class AEDArgs(object):
    server = None
    username = None
    begin_date = None
    end_date = None
    ignore_ssl_errors = False
    output_format = "JSON"
    record_cursor = False
    exposure_types = None
    debug_mode = False
    destination_type = "stdout"
    destination = None
    syslog_port = 514
    syslog_protocol = "TCP"


def _union_cli_args_with_config_args(cli_args, config_parser):
    args = AEDArgs()
    args.server = (
        cli_args.c42_authority_url if cli_args.c42_authority_url else config_parser.get("server")
    )
    args.username = (
        cli_args.c42_username if cli_args.c42_username else config_parser.get("username")
    )
    args.begin_date = (
        cli_args.c42_begin_date if cli_args.c42_begin_date else config_parser.get("begin_date")
    )

    if args.begin_date is None:
        args.begin_date = _get_default_begin_date()

    args.end_date = (
        cli_args.c42_end_date if cli_args.c42_end_date else config_parser.get("end_date")
    )

    if args.end_date is None:
        args.end_date = _get_default_end_date()

    args.ignore_ssl_errors = (
        cli_args.c42_ignore_ssl_errors
        if cli_args.c42_ignore_ssl_errors
        else config_parser.get("ignore_ssl_errors")
    )
    args.output_format = (
        cli_args.c42_output_format
        if cli_args.c42_output_format
        else config_parser.get("output_format")
    )
    args.record_cursor = (
        cli_args.c42_record_cursor
        if cli_args.c42_record_cursor
        else config_parser.get("record_cursor")
    )
    args.exposure_types = (
        cli_args.c42_exposure_types
        if cli_args.c42_exposure_types
        else config_parser.get("exposure_types")
    )
    args.debug_mode = (
        cli_args.c42_debug_mode if cli_args.c42_debug_mode else config_parser.get("debug_mode")
    )
    args.destination_type = (
        cli_args.c42_destination_type
        if cli_args.c42_destination_type
        else config_parser.get("destination_type")
    )
    args.destination = (
        cli_args.c42_destination if cli_args.c42_destination else config_parser.get("destination")
    )
    args.syslog_port = (
        cli_args.c42_syslog_port if cli_args.c42_syslog_port else config_parser.get("syslog_port")
    )
    args.syslog_protocol = (
        cli_args.c42_syslog_protocol
        if cli_args.c42_syslog_protocol
        else config_parser.get("syslog_protocol")
    )
    return args


def _get_default_begin_date():
    default_begin_date = datetime.now() - timedelta(days=60)
    return default_begin_date.strftime("%Y-%m-%d")


def _get_default_end_date():
    default_end_date = datetime.now()
    return default_end_date.strftime("%Y-%m-%d")


def _ignore_ssl_errors():
    settings.verify_ssl_certs = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _parse_min_timestamp(args):
    min_timestamp = parse_timestamp(args.begin_date)
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp < boundary:
        print("Argument --begin must be within 90 days")
        exit(1)

    return min_timestamp


def _create_sdk_from_args(args, parser):
    server = _get_server_from_args(args, parser)
    username = _get_username_from_args(args, parser)
    password = _get_password(username)
    sdk = SDK.create_using_local_account(host_address=server, username=username, password=password)
    return sdk


def _get_server_from_args(args, parser):
    server = args.server
    if server is None:
        _exit_from_argument_error("Host address not provided.", parser)

    return server


def _get_username_from_args(args, parser):
    username = args.username
    if username is None:
        _exit_from_argument_error("Username not provided.", parser)

    return username


def _exit_from_argument_error(message, parser):
    print(message)
    parser.print_usage()
    exit(1)


def _get_password(username):
    password = get_password(_SERVICE_NAME_FOR_KEYCHAIN, username)
    if password is None:
        pwd = getpass()
        set_password(_SERVICE_NAME_FOR_KEYCHAIN, username, pwd)

    return password


def _create_handlers(args):
    store = AEDCursorStore()
    handlers = FileEventHandlers()
    handlers.record_cursor_position = store.replace_stored_insertion_timestamp
    handlers.get_cursor_position = store.get_stored_insertion_timestamp
    output_format = args.output_format
    destination = args.destination
    logger_formatter = _get_log_formatter(output_format)
    logger = get_logger(logger_formatter, destination)
    handlers.handle_response = _get_response_handler(logger)
    return handlers


def _get_log_formatter(output_format):
    if output_format == "JSON":
        return AEDDictToJSONFormatter()
    elif output_format == "CEF":
        return AEDDictToCEFFormatter()
    else:
        print("Unsupported output format {0}".format(output_format))
        exit(1)


def _get_response_handler(logger):
    def handle_response(response):
        response_dict = json.loads(response.text)
        file_events_key = u"fileEvents"
        if file_events_key in response_dict:
            events = response_dict[file_events_key]
            for event in events:
                logger.info(event)

    return handle_response


if __name__ == "__main__":
    main()
