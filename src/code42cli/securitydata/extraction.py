from __future__ import print_function
import json
from py42.sdk import SDK
from py42 import debug_level
from py42 import settings
from c42eventextractor import FileEventHandlers
from c42eventextractor.extractors import FileEventExtractor
from py42.sdk.file_event_query.cloud_query import Actor
from py42.sdk.file_event_query.device_query import DeviceUsername
from py42.sdk.file_event_query.event_query import Source
from py42.sdk.file_event_query.exposure_query import ExposureType, ProcessOwner, TabURL
from py42.sdk.file_event_query.file_query import MD5, SHA256, FileName, FilePath

from code42cli.compat import str
from code42cli.util import print_error, print_bold, is_interactive
from code42cli.profile.profile import get_profile
from code42cli.securitydata.options import ExposureType as ExposureTypeOptions
from code42cli.securitydata import date_helper as date_helper
from code42cli.securitydata.cursor_store import AEDCursorStore
from code42cli.securitydata.logger_factory import get_error_logger
from code42cli.securitydata.arguments.search import SearchArguments
from code42cli.securitydata.arguments.main import IS_INCREMENTAL_KEY


_EXCEPTIONS_OCCURRED = False


def extract(output_logger, args):
    """Extracts file events using the given command-line arguments.

        Args:
            output_logger: The logger specified by which subcommand you use. For example,
                print: uses a logger that streams to stdout.
                write-to: uses a logger that logs to a file.
                send-to: uses a logger that sends logs to a server.
            args:
                Command line args used to build up file event query filters.
    """
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
    if is_debug_mode:
        settings.debug_level = debug_level.DEBUG
    try:
        return SDK.create_using_local_account(
            profile.authority_url, profile.username, profile.get_password()
        )
    except:
        print_error(
            u"Invalid credentials or host address. "
            u"Verify your profile is set up correctly and that you are supplying the correct password."
        )
        exit(1)


def _call_extract(extractor, args):
    if not _determine_if_advanced_query(args):
        _verify_begin_date(args.begin_date)
        _verify_exposure_types(args.exposure_types)
        filters = _create_filters(args)
        extractor.extract(*filters)
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


def _verify_begin_date(begin_date):
    if not begin_date:
        print_error(u"'begin date' is required.")
        print(u"")
        print_bold(u"Try using  '-b' or '--begin'. Use `-h` for more info.")
        print(u"")
        exit(1)


def _verify_exposure_types(exposure_types):
    if exposure_types is None:
        return
    options = list(ExposureTypeOptions())
    for exposure_type in exposure_types:
        if exposure_type not in options:
            print_error(u"'{0}' is not a valid exposure type.".format(exposure_type))
            exit(1)


def _handle_result():
    if is_interactive() and _EXCEPTIONS_OCCURRED:
        print_error(u"View exceptions that occurred at [HOME]/.code42cli/log/code42_errors.")


def _create_filters(args):
    filters = [_get_event_timestamp_filter(args)]
    not args.c42username or filters.append(DeviceUsername.eq(args.c42username))
    not args.actor or filters.append(Actor.eq(args.actor))
    not args.md5 or filters.append(MD5.eq(args.md5))
    not args.sha256 or filters.append(SHA256.eq(args.sha256))
    not args.source or filters.append(Source.eq(args.source))
    not args.filename or filters.append(FileName.eq(args.filename))
    not args.filepath or filters.append(FilePath.eq(args.filepath))
    not args.process_owner or filters.append(ProcessOwner.eq(args.process_owner))
    not args.tab_url or filters.append(TabURL.eq(args.tab_url))
    _try_append_exposure_types_filter(filters, args)
    return filters


def _try_append_exposure_types_filter(filters, args):
    exposure_filter = _create_exposure_type_filter(args)
    if exposure_filter:
        filters.append(exposure_filter)


def _create_exposure_type_filter(args):
    if args.include_non_exposure_events and args.exposure_types:
        print_error(u"Cannot use exposure types with `--include-non-exposure`.")
        exit(1)
    if args.exposure_types:
        return ExposureType.is_in(args.exposure_types)
    if not args.include_non_exposure_events:
        return ExposureType.exists()
