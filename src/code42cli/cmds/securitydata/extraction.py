from __future__ import print_function

import json

from c42eventextractor import FileEventHandlers
from c42eventextractor.extractors import FileEventExtractor
from py42.sdk.queries.fileevents.filters import *

import code42cli.cmds.securitydata.date_helper as date_helper
from code42cli.cmds.securitydata.enums import (
    ExposureType as ExposureTypeOptions,
    IS_INCREMENTAL_KEY,
    SearchArguments,
)
from code42cli.logger import get_error_logger
from code42cli.cmds.shared.cursor_store import FileEventCursorStore
from code42cli.compat import str
from code42cli.util import is_interactive, print_bold, print_error, print_to_stderr
import code42cli.errors as errors


_TOTAL_EVENTS = 0


def extract(sdk, profile, output_logger, args):
    """Extracts file events using the given command-line arguments.

        Args:
            sdk (py42.sdk.SDKClient): The py42 sdk.
            profile (Code42Profile): The profile under which to execute this command.
            output_logger (Logger): The logger specified by which subcommand you use. For example,
                print: uses a logger that streams to stdout.
                write-to: uses a logger that logs to a file.
                send-to: uses a logger that sends logs to a server.
            args: Command line args used to build up file event query filters.
    """
    store = _create_cursor_store(args, profile)
    filters = _get_filters(args, store)
    handlers = _create_event_handlers(output_logger, store)
    extractor = FileEventExtractor(sdk, handlers)
    _call_extract(extractor, filters, args.advanced_query)
    _handle_result()


def _create_cursor_store(args, profile):
    if args.incremental:
        return FileEventCursorStore(profile.name)


def _get_filters(args, cursor_store):
    if not _determine_if_advanced_query(args):
        _verify_begin_date_requirements(args, cursor_store)
        _verify_exposure_types(args.type)
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
    if _begin_date_is_required(args, cursor_store) and not args.begin:
        print_error(u"'begin date' is required.")
        print(u"")
        print_bold(u"Try using  '-b' or '--begin'. Use `-h` for more info.")
        print(u"")
        exit(1)


def _begin_date_is_required(args, cursor_store):
    if not args.incremental:
        return True
    is_required = cursor_store and cursor_store.get_stored_insertion_timestamp() is None

    # Ignore begin date when is incremental mode, it is not required, and it was passed an argument.
    if not is_required and args.begin:
        args.begin = None
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
    event_timestamp_filter = _get_event_timestamp_filter(args.begin, args.end)
    not event_timestamp_filter or filters.append(event_timestamp_filter)
    not args.c42_username or filters.append(DeviceUsername.is_in(args.c42_username))
    not args.actor or filters.append(Actor.is_in(args.actor))
    not args.md5 or filters.append(MD5.is_in(args.md5))
    not args.sha256 or filters.append(SHA256.is_in(args.sha256))
    not args.source or filters.append(Source.is_in(args.source))
    not args.file_name or filters.append(FileName.is_in(args.file_name))
    not args.file_path or filters.append(FilePath.is_in(args.file_path))
    not args.process_owner or filters.append(ProcessOwner.is_in(args.process_owner))
    not args.tab_url or filters.append(TabURL.is_in(args.tab_url))
    _try_append_exposure_types_filter(filters, args.include_non_exposure, args.type)
    return filters


def _get_event_timestamp_filter(begin_date, end_date):
    try:
        begin_date = begin_date.strip() if begin_date else None
        end_date = end_date.strip() if end_date else None
        return date_helper.create_event_timestamp_filter(begin_date, end_date)
    except date_helper.DateArgumentException as ex:
        print_error(str(ex))
        exit(1)


def _create_event_handlers(output_logger, cursor_store):
    handlers = FileEventHandlers()
    error_logger = get_error_logger()

    def handle_error(exception):
        error_logger.error(exception)
        errors.ERRORED = True

    handlers.handle_error = handle_error

    if cursor_store:
        handlers.record_cursor_position = cursor_store.replace_stored_insertion_timestamp
        handlers.get_cursor_position = cursor_store.get_stored_insertion_timestamp

    def handle_response(response):
        response_dict = json.loads(response.text)
        events = response_dict.get(u"fileEvents")
        global _TOTAL_EVENTS
        _TOTAL_EVENTS += len(events)
        for event in events:
            output_logger.info(event)

    handlers.handle_response = handle_response
    return handlers


def _call_extract(extractor, filters, advanced_query):
    if advanced_query:
        extractor.extract_advanced(advanced_query)
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
    # Have to call this explicitly (instead of relying on invoker) because errors are caught in
    # `c42eventextractor`.
    errors.print_errors_occurred_if_needed()
    if not _TOTAL_EVENTS:
        print_to_stderr(u"No results found\n")


def _try_append_exposure_types_filter(filters, include_non_exposure_events, exposure_types):
    _exposure_filter = _create_exposure_type_filter(include_non_exposure_events, exposure_types)
    if _exposure_filter:
        filters.append(_exposure_filter)


def _create_exposure_type_filter(include_non_exposure_events, exposure_types):
    if include_non_exposure_events and exposure_types:
        print_error(u"Cannot use exposure types with `--include-non-exposure`.")
        exit(1)
    if exposure_types:
        return ExposureType.is_in(exposure_types)
    if not include_non_exposure_events:
        return ExposureType.exists()
