from __future__ import print_function
import json
from datetime import datetime, timedelta
from py42.sdk import SDK
from py42 import debug_level
from py42 import settings
from c42eventextractor.common import FileEventHandlers
from c42eventextractor.extractors import AEDEventExtractor
from c42eventextractor.common import convert_datetime_to_timestamp

from code42cli.securitydata.options import ExposureType
from code42cli.util import print_error
from code42cli.securitydata.cursor_store import AEDCursorStore
from code42cli.securitydata.logger_factory import get_error_logger
from code42cli.profile.profile import get_profile
from code42cli.securitydata.arguments.search import SearchArguments
from code42cli.securitydata.arguments.main import IS_INCREMENTAL_KEY


def extract(output_logger, args):
    handlers = _create_event_handlers(output_logger, args.is_incremental)
    profile = get_profile()
    sdk = _get_sdk(profile, args.is_debug_mode)
    extractor = AEDEventExtractor(sdk, handlers)
    _call_extract(extractor, args)


def _create_event_handlers(output_logger, is_incremental):
    handlers = FileEventHandlers()
    error_logger = get_error_logger()
    handlers.handle_error = error_logger.error
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


def _parse_min_timestamp(begin_date):
    min_timestamp = _parse_timestamp(begin_date)
    boundary_date = datetime.utcnow() - timedelta(days=90)
    boundary = convert_datetime_to_timestamp(boundary_date)
    if min_timestamp and min_timestamp < boundary:
        print("Argument '--begin' must be within 90 days.")
        exit(1)
    return min_timestamp


def _parse_timestamp(input_string):
    try:
        # Input represents date str like '2020-02-13'
        time = datetime.strptime(input_string, "%Y-%m-%d")
    except ValueError:
        # Input represents amount of seconds ago like '86400'
        if input_string and input_string.isdigit():
            now = datetime.utcnow()
            time = now - timedelta(minutes=int(input_string))
        else:
            raise ValueError("input must be a positive integer or a date in YYYY-MM-DD format.")

    return convert_datetime_to_timestamp(time)


def _call_extract(extractor, args):
    if not _determine_if_advanced_query(args):
        min_timestamp = _parse_min_timestamp(args.begin_date) if args.begin_date else None
        max_timestamp = _parse_timestamp(args.end_date) if args.end_date else None
        _verify_exposure_types(args.exposure_types)
        _verify_timestamp_order(min_timestamp, max_timestamp)
        extractor.extract(
            initial_min_timestamp=min_timestamp,
            max_timestamp=max_timestamp,
            exposure_types=args.exposure_types,
        )
    else:
        extractor.extract_raw(args.advanced_query)


def _determine_if_advanced_query(args):
    if args.advanced_query is not None:
        given_args = vars(args)
        for key in given_args:
            val = given_args[key]
            if not _verify_compatibility_with_advanced_query(key, val):
                print_error("You cannot use --advanced-query with additional search args.")
                exit(1)
        return True
    return False


def _verify_compatibility_with_advanced_query(key, val):
    if val is not None:
        is_other_search_arg = key in SearchArguments() and key != SearchArguments.ADVANCED_QUERY
        is_incremental = key == IS_INCREMENTAL_KEY and val
        return not is_other_search_arg and not is_incremental
    return True


def _verify_exposure_types(exposure_types):
    if exposure_types is None:
        return
    options = list(ExposureType())
    for exposure_type in exposure_types:
        if exposure_type not in options:
            print_error("'{0}' is not a valid exposure type.".format(exposure_type))
            exit(1)


def _verify_timestamp_order(begin_timestamp, end_timestamp):
    if begin_timestamp is None or end_timestamp is None:
        return

    if begin_timestamp >= end_timestamp:
        print_error("Begin date cannot be after end date")
        exit(1)
