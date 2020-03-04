from __future__ import print_function
import json
from py42.sdk import SDK
from py42 import debug_level
from py42 import settings
from c42eventextractor import FileEventHandlers
from c42eventextractor.extractors import FileEventExtractor

from code42cli.compat import str
from code42cli.securitydata.options import ExposureType
from code42cli.util import print_error, is_interactive
from code42cli import date_helper as date_helper
from code42cli.securitydata.cursor_store import AEDCursorStore
from code42cli.securitydata.logger_factory import get_error_logger
from code42cli.profile.profile import get_profile
from code42cli.securitydata.arguments.search import SearchArguments
from code42cli.securitydata.arguments.main import IS_INCREMENTAL_KEY


_EXCEPTIONS_OCCURRED = False


def extract(output_logger, args):
    handlers = _create_event_handlers(output_logger, args.is_incremental)
    profile = get_profile()
    sdk = _get_sdk(profile, args.is_debug_mode)
    extractor = FileEventExtractor(sdk, handlers)
    _call_extract(extractor, args)
    _handle_result()


def _create_event_handlers(output_logger, is_incremental):
    handlers = FileEventHandlers()
    error_logger = get_error_logger()

    def handle_error(exception):
        error_logger.error(exception)
        global _EXCEPTIONS_OCCURRED
        _EXCEPTIONS_OCCURRED = True

    handlers.handle_error = handle_error

    if is_incremental:
        store = AEDCursorStore()
        handlers.record_cursor_position = store.replace_stored_insertion_timestamp
        handlers.get_cursor_position = store.get_stored_insertion_timestamp

    def handle_response(response):
        response_dict = json.loads(response.text)
        events = response_dict.get(u"fileEvents")
        for event in events:
            output_logger.info(event)

    handlers.handle_response = handle_response
    return handlers


def _get_sdk(profile, is_debug_mode):
    code42 = SDK.create_using_local_account(
        profile.authority_url, profile.username, profile.get_password()
    )
    if is_debug_mode:
        settings.debug_level = debug_level.DEBUG
    return code42


def _call_extract(extractor, args):
    if not _determine_if_advanced_query(args):
        event_timestamp_filter_group = _get_event_timestamp_filter(args)
        _verify_exposure_types(args.exposure_types)
        extractor.extract(args.exposure_types, event_timestamp_filter_group)
    else:
        extractor.extract_advanced(args.advanced_query)


def _determine_if_advanced_query(args):
    if args.advanced_query is not None:
        given_args = vars(args)
        for key in given_args:
            val = given_args[key]
            if not _verify_compatibility_with_advanced_query(key, val):
                print_error(u"You cannot use --advanced-query with additional search args.")
                exit(1)
        return True
    return False


def _verify_compatibility_with_advanced_query(key, val):
    if val is not None:
        is_other_search_arg = key in SearchArguments() and key != SearchArguments.ADVANCED_QUERY
        is_incremental = key == IS_INCREMENTAL_KEY and val
        return not is_other_search_arg and not is_incremental
    return True


def _get_event_timestamp_filter(args):
    try:
        return date_helper.create_event_timestamp_range(args.begin_date, args.end_date)
    except ValueError as ex:
        print_error(str(ex))
        exit(1)


def _verify_exposure_types(exposure_types):
    if exposure_types is None:
        return
    options = list(ExposureType())
    for exposure_type in exposure_types:
        if exposure_type not in options:
            print_error(u"'{0}' is not a valid exposure type.".format(exposure_type))
            exit(1)


def _handle_result(args):
    if args.silence_result_status:
        return
    if not  is_interactive() and _EXCEPTIONS_OCCURRED:
        print_error("View exceptions that occurred at [HOME]/.code42cli/log/code42_errors.")
    else:
        print("Command succeeded with no errors.")
