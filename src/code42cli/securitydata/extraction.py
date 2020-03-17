from __future__ import print_function

import json

from c42eventextractor import FileEventHandlers
from c42eventextractor.extractors import FileEventExtractor
from py42.sdk.queries.fileevents.filters import *

from code42cli.compat import str
from code42cli.profile.profile import get_profile
from code42cli.sdk_client import create_sdk
from code42cli.securitydata import date_helper as date_helper
from code42cli.securitydata.arguments.main import IS_INCREMENTAL_KEY
from code42cli.securitydata.arguments.search import SearchArguments
from code42cli.securitydata.cursor_store import FileEventCursorStore
from code42cli.securitydata.logger_factory import get_error_logger
from code42cli.securitydata.options import ExposureType as ExposureTypeOptions
from code42cli.util import print_error, print_bold, is_interactive

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
    profile = get_profile(args.profile_name)
    store = _create_cursor_store(args, profile)
    filters = _get_filters(args, store)
    handlers = _create_event_handlers(output_logger, store)
    sdk = create_sdk(profile, args.is_debug_mode)
    extractor = FileEventExtractor(sdk, handlers)
    _call_extract(extractor, filters, args)
    _handle_result()


def _create_cursor_store(args, profile):
    if args.is_incremental:
        return FileEventCursorStore(profile.name)


def _get_filters(args, cursor_store):
    if not _determine_if_advanced_query(args):
        _verify_begin_date_requirements(args, cursor_store)
        _verify_exposure_types(args.exposure_types)
        return _create_filters(args)
    else:
        return args.advanced_query


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


def _verify_begin_date_requirements(args, cursor_store):
    if _begin_date_is_required(args, cursor_store) and not args.begin_date:
        print_error(u"'begin date' is required.")
        print(u"")
        print_bold(u"Try using  '-b' or '--begin'. Use `-h` for more info.")
        print(u"")
        exit(1)


def _begin_date_is_required(args, cursor_store):
    if not args.is_incremental:
        return True
    is_required = cursor_store and cursor_store.get_stored_insertion_timestamp() is None

    # Ignore begin date when is incremental mode, it is not required, and it was passed an argument.
    if not is_required and args.begin_date:
        args.begin_date = None
    return is_required


def _verify_exposure_types(exposure_types):
    if exposure_types is None:
        return
    options = list(ExposureTypeOptions())
    for exposure_type in exposure_types:
        if exposure_type not in options:
            print_error(u"'{0}' is not a valid exposure type.".format(exposure_type))
            exit(1)


def _create_filters(args):
    filters = []
    event_timestamp_filter = _get_event_timestamp_filter(args)
    not event_timestamp_filter or filters.append(event_timestamp_filter)
    not args.c42usernames or filters.append(DeviceUsername.is_in(args.c42usernames))
    not args.actors or filters.append(Actor.is_in(args.actors))
    not args.md5_hashes or filters.append(MD5.is_in(args.md5_hashes))
    not args.sha256_hashes or filters.append(SHA256.is_in(args.sha256_hashes))
    not args.sources or filters.append(Source.is_in(args.sources))
    not args.filenames or filters.append(FileName.is_in(args.filenames))
    not args.filepaths or filters.append(FilePath.is_in(args.filepaths))
    not args.process_owners or filters.append(ProcessOwner.is_in(args.process_owners))
    not args.tab_urls or filters.append(TabURL.is_in(args.tab_urls))
    _try_append_exposure_types_filter(filters, args)
    return filters


def _get_event_timestamp_filter(args):
    try:
        begin_date = args.begin_date.strip().split(" ") if args.begin_date else None
        end_date = args.end_date.strip().split(" ") if args.end_date else None
        return date_helper.create_event_timestamp_filter(begin_date, end_date)
    except ValueError as ex:
        print_error(str(ex))
        exit(1)


def _create_event_handlers(output_logger, cursor_store):
    handlers = FileEventHandlers()
    error_logger = get_error_logger()

    def handle_error(exception):
        error_logger.error(exception)
        global _EXCEPTIONS_OCCURRED
        _EXCEPTIONS_OCCURRED = True

    handlers.handle_error = handle_error

    if cursor_store:
        handlers.record_cursor_position = cursor_store.replace_stored_insertion_timestamp
        handlers.get_cursor_position = cursor_store.get_stored_insertion_timestamp

    def handle_response(response):
        response_dict = json.loads(response.text)
        events = response_dict.get(u"fileEvents")
        for event in events:
            output_logger.info(event)

    handlers.handle_response = handle_response
    return handlers


def _call_extract(extractor, filters, args):
    if args.advanced_query:
        extractor.extract_advanced(args.advanced_query)
    else:
        extractor.extract(*filters)


def _verify_compatibility_with_advanced_query(key, val):
    if key == SearchArguments.INCLUDE_NON_EXPOSURE_EVENTS and not val:
        return True

    if val is not None:
        is_other_search_arg = key in SearchArguments() and key != SearchArguments.ADVANCED_QUERY
        is_incremental = key == IS_INCREMENTAL_KEY and val
        return not is_other_search_arg and not is_incremental
    return True


def _handle_result():
    if is_interactive() and _EXCEPTIONS_OCCURRED:
        print_error(u"View exceptions that occurred at [HOME]/.code42cli/log/code42_errors.")


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
