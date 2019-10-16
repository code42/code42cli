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
from c42seceventcli.aed.cursor_store import AEDCursorStore
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
    config_args = SecurityEventConfigParser("config.cfg")
    args = _union_cli_args_with_config_args(cli_args, config_args)

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


def _union_cli_args_with_config_args(cli_args, config_args):
    args = AEDArgs()
    server = _select_arg(cli_args.c42_authority_url, config_args.get("server"))
    _set_arg_attr(args, "server", server)
    username = _select_arg(cli_args.c42_username, config_args.get("username"))
    _set_arg_attr(args, "username", username)
    begin_date = _select_arg(cli_args.c42_begin_date, config_args.get("begin_date"))
    _set_arg_attr(args, "begin_date", begin_date, _get_default_begin_date)
    end_date = _select_arg(cli_args.c42_end_date, config_args.get("end_date"))
    _set_arg_attr(args, "end_date", end_date, _get_default_end_date)
    ignore_ssl_errors = _select_arg(
        cli_args.c42_ignore_ssl_errors, config_args.get_bool("ignore_ssl_errors")
    )
    _set_arg_attr(args, "ignore_ssl_errors", ignore_ssl_errors)
    output_format = _select_arg(cli_args.c42_output_format, config_args.get("output_format"))
    _set_arg_attr(args, "output_format", output_format)
    record_cursor = _select_arg(cli_args.c42_record_cursor, config_args.get_bool("record_cursor"))
    _set_arg_attr(args, "record_cursor", record_cursor)
    exposure_types = _select_arg(cli_args.c42_exposure_types, config_args.get("exposure_types"))
    _set_arg_attr(args, "exposure_types", exposure_types)
    debug_mode = _select_arg(cli_args.c42_debug_mode, config_args.get_bool("debug_mode"))
    _set_arg_attr(args, "debug_mode", debug_mode)
    dest_type = _select_arg(cli_args.c42_destination_type, config_args.get("destination_type"))
    _set_arg_attr(args, "destination_type", dest_type)
    dest = _select_arg(cli_args.c42_destination, config_args.get("destination"))
    _set_arg_attr(args, "destination", dest)
    syslog_port = _select_arg(cli_args.c42_syslog_port, config_args.get_int("syslog_port"))
    _set_arg_attr(args, "syslog_port", syslog_port)
    syslog_protocol = _select_arg(cli_args.c42_syslog_protocol, config_args.get("syslog_protocol"))
    _set_arg_attr(args, "syslog_protocol", syslog_protocol)
    return args


def _select_arg(cli_arg, config_arg):
    return cli_arg if cli_arg is not None else config_arg


def _set_arg_attr(args, name, value, get_default_value=None):
    if value is not None:
        setattr(args, name, value)
    elif get_default_value is not None:
        default_value = get_default_value()
        setattr(args, name, default_value)


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
