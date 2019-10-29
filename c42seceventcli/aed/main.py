import json
from socket import gaierror, herror, timeout
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta

from py42 import debug_level
from py42 import settings
from py42.sdk import SDK
from c42secevents.extractors import AEDEventExtractor
from c42secevents.common import FileEventHandlers, convert_datetime_to_timestamp
from c42secevents.logging.formatters import AEDDictToCEFFormatter, AEDDictToJSONFormatter

import c42seceventcli.common.util as common
import c42seceventcli.aed.args as aed_args
from c42seceventcli.aed.cursor_store import AEDCursorStore

_SERVICE_NAME = u"c42seceventcli_aed"


def main():
    args = _get_args()
    if args.reset_password:
        common.delete_stored_password(_SERVICE_NAME, args.c42_username)

    handlers = _create_handlers(args)
    _set_up_cursor_store(
        record_cursor=args.record_cursor, clear_cursor=args.clear_cursor, handlers=handlers
    )
    sdk = _create_sdk_from_args(args, handlers)

    if bool(args.ignore_ssl_errors):
        _ignore_ssl_errors()

    if bool(args.debug_mode):
        settings.debug_level = debug_level.DEBUG

    _extract(args=args, sdk=sdk, handlers=handlers)


def _get_args():
    try:
        return aed_args.get_args()
    except ValueError as ex:
        print(repr(ex))
        exit(1)


def _ignore_ssl_errors():
    settings.verify_ssl_certs = False
    disable_warnings(InsecureRequestWarning)


def _create_handlers(args):
    handlers = FileEventHandlers()
    error_logger = common.get_error_logger(_SERVICE_NAME)
    settings.global_exception_message_receiver = error_logger.error
    handlers.handle_error = error_logger.error
    output_format = args.output_format
    logger_formatter = _get_log_formatter(output_format)
    logger = _get_logger(
        formatter=logger_formatter,
        service_name=_SERVICE_NAME,
        destination=args.destination,
        destination_type=args.destination_type,
        destination_port=int(args.destination_port),
        destination_protocol=args.destination_protocol,
    )
    handlers.handle_response = _get_response_handler(logger)
    return handlers


def _get_logger(
    formatter,
    service_name,
    destination,
    destination_type,
    destination_port=514,
    destination_protocol="TCP",
):
    try:
        return common.get_logger(
            formatter=formatter,
            service_name=service_name,
            destination=destination,
            destination_type=destination_type,
            destination_port=destination_port,
            destination_protocol=destination_protocol,
        )
    except (herror, gaierror, timeout) as ex:
        print(repr(ex))
        print(
            "Hostname={0}, port={1}, protocol={2}.".format(
                destination, destination_port, destination_protocol
            )
        )
        exit(1)
    except IOError as ex:
        print(repr(ex))
        print("File path: {0}.".format(destination))
        exit(1)


def _set_up_cursor_store(record_cursor, clear_cursor, handlers):
    if record_cursor or clear_cursor:
        store = AEDCursorStore()
        if clear_cursor:
            store.reset()

        if record_cursor:
            handlers.record_cursor_position = store.replace_stored_insertion_timestamp
            handlers.get_cursor_position = store.get_stored_insertion_timestamp
            return store


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


def _create_sdk_from_args(args, handlers):
    password = common.get_stored_password(_SERVICE_NAME, args.c42_username)
    try:
        sdk = SDK.create_using_local_account(
            host_address=args.c42_authority_url, username=args.c42_username, password=password
        )
        return sdk
    except Exception as ex:
        handlers.handle_error(ex)
        print("Incorrect username or password.")
        exit(1)


def _extract(args, sdk, handlers):
    min_timestamp = _parse_min_timestamp(args.begin_date)
    max_timestamp = common.parse_timestamp(args.end_date)
    extractor = AEDEventExtractor(sdk, handlers)
    extractor.extract(min_timestamp, max_timestamp, args.exposure_types)


def _parse_min_timestamp(begin_date):
    min_timestamp = common.parse_timestamp(begin_date)
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp < boundary:
        print("Argument '--begin' must be within 90 days.")
        exit(1)

    return min_timestamp


if __name__ == "__main__":
    main()
