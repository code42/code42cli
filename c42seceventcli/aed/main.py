import json
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from argparse import ArgumentParser
from datetime import datetime, timedelta
from keyring import get_password, set_password, delete_password
from keyring.errors import PasswordDeleteError
from getpass import getpass

from py42 import debug_level
from py42 import settings
from py42.sdk import SDK
from c42secevents.extractors import AEDEventExtractor
from c42secevents.common import FileEventHandlers, convert_datetime_to_timestamp
from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter

from c42seceventcli.common.common import (
    get_config_args,
    parse_timestamp,
    get_logger,
    get_error_logger,
)
from c42seceventcli.aed.cursor_store import AEDCursorStore
from c42seceventcli.common.cli_args import (
    add_clear_cursor_arg,
    add_reset_password_arg,
    add_config_file_path_arg,
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
    cli_args = vars(parser.parse_args())

    config_args = get_config_args(cli_args.get("c42_config_file"))
    args = _create_args(cli_args, config_args)

    if cli_args.get("c42_reset_password"):
        _delete_stored_password(args.c42_username)

    _verify_destination_args(args)
    store = AEDCursorStore()
    handlers = _create_handlers(args, store)
    sdk = _create_sdk_from_args(args, parser, handlers)

    if cli_args.get("c42_clear_cursor"):
        store.reset()

    if bool(args.c42_ignore_ssl_errors):
        _ignore_ssl_errors()

    if bool(args.c42_debug_mode):
        settings.debug_level = debug_level.DEBUG

    _extract(args=args, sdk=sdk, handlers=handlers)


def _get_arg_parser():
    parser = ArgumentParser(add_help=False)

    # Makes sure that you can't give both an end_timestamp and record cursor positions
    mutually_exclusive_timestamp_group = parser.add_mutually_exclusive_group()
    add_end_date_arg(mutually_exclusive_timestamp_group)
    add_record_cursor_arg(mutually_exclusive_timestamp_group)

    main_args = parser.add_argument_group("main")
    add_clear_cursor_arg(main_args)
    add_reset_password_arg(main_args)
    add_config_file_path_arg(main_args)
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


def _create_args(cli_args, config_args):
    args = AEDArgs()
    keys = cli_args.keys()
    for key in keys:
        args.try_set(key, cli_args.get(key), config_args.get(key))

    return args


class AEDArgs(object):
    c42_authority_url = None
    c42_username = None
    c42_begin_date = None
    c42_end_date = None
    c42_ignore_ssl_errors = False
    c42_output_format = "JSON"
    c42_record_cursor = False
    c42_exposure_types = None
    c42_debug_mode = False
    c42_destination_type = "stdout"
    c42_destination = None
    c42_syslog_port = 514
    c42_syslog_protocol = "TCP"

    def __init__(self):
        self.c42_begin_date = AEDArgs._get_default_begin_date()
        self.c42_end_date = AEDArgs._get_default_end_date()

    def try_set(self, arg_name, cli_arg=None, config_arg=None):
        if cli_arg is not None:
            setattr(self, arg_name, cli_arg)
        elif config_arg is not None:
            setattr(self, arg_name, config_arg)

    @staticmethod
    def _get_default_begin_date():
        default_begin_date = datetime.now() - timedelta(days=60)
        return default_begin_date.strftime("%Y-%m-%d")

    @staticmethod
    def _get_default_end_date():
        default_end_date = datetime.now()
        return default_end_date.strftime("%Y-%m-%d")


def _delete_stored_password(username):
    try:
        delete_password(_SERVICE_NAME_FOR_KEYCHAIN, username)
    except PasswordDeleteError:
        return


def _ignore_ssl_errors():
    settings.verify_ssl_certs = False
    disable_warnings(InsecureRequestWarning)


def _create_handlers(args, store):
    handlers = FileEventHandlers()
    error_logger = get_error_logger()
    settings.global_exception_message_receiver = error_logger.error
    handlers.handle_exception = error_logger.error

    if bool(args.c42_record_cursor):
        handlers.record_cursor_position = store.replace_stored_insertion_timestamp
        handlers.get_cursor_position = store.get_stored_insertion_timestamp

    output_format = args.c42_output_format
    logger_formatter = _get_log_formatter(output_format)
    logger = get_logger(
        formatter=logger_formatter,
        destination=args.c42_destination,
        destination_type=args.c42_destination_type,
        syslog_port=int(args.c42_syslog_port),
        syslog_protocol=args.c42_syslog_protocol,
    )
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


def _create_sdk_from_args(args, parser, handlers):
    server = _get_server_from_args(args, parser)
    username = _get_username_from_args(args, parser)
    password = _get_password(username)
    try:
        sdk = SDK.create_using_local_account(
            host_address=server, username=username, password=password
        )
        return sdk
    except Exception as ex:
        handlers.handle_exception(ex)
        print("Incorrect username or password.")
        exit(1)


def _get_server_from_args(args, parser):
    server = args.c42_authority_url
    if server is None:
        _exit_from_argument_error("Host address not provided.", parser)

    return server


def _get_username_from_args(args, parser):
    username = args.c42_username
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
        try:
            password = getpass(prompt="Code42 password: ")
        except KeyboardInterrupt:
            print()
            exit(1)

        set_password(_SERVICE_NAME_FOR_KEYCHAIN, username, password)

    return password


def _verify_destination_args(args):
    if args.c42_destination_type == "stdout" and args.c42_destination is not None:
        print(
            "Ambiguous destination '{0}' for '{1}' destination type.".format(
                args.c42_destination, args.c42_destination_type
            )
        )
        exit(1)

    if args.c42_destination_type == "file" and args.c42_destination is None:
        print("Missing file name. Try: '--dest path/to/file'.")
        exit(1)

    if args.c42_destination_type == "syslog" and args.c42_destination is None:
        print("Missing syslog server URL. Try: '--dest https://syslog.example.com'.")
        exit(1)


def _extract(args, sdk, handlers):
    min_timestamp = _parse_min_timestamp(args.c42_begin_date)
    max_timestamp = parse_timestamp(args.c42_end_date)
    extractor = AEDEventExtractor(sdk, handlers)
    extractor.extract(min_timestamp, max_timestamp, args.c42_exposure_types)


def _parse_min_timestamp(begin_date):
    min_timestamp = parse_timestamp(begin_date)
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp < boundary:
        print("Argument --begin must be within 90 days.")
        exit(1)

    return min_timestamp


if __name__ == "__main__":
    main()
