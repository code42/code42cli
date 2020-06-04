from c42eventextractor.extractors import FileEventExtractor
from py42.sdk.queries.fileevents.filters import *

from code42cli.cmds.search_shared.enums import (
    ExposureType as ExposureTypeOptions,
    FileEventFilterArguments,
)
from code42cli.cmds.search_shared.cursor_store import FileEventCursorStore
from code42cli.cmds.search_shared.extraction import (
    verify_begin_date_requirements,
    create_handlers,
    exit_if_advanced_query_used_with_other_search_args,
    create_time_range_filter,
)
import code42cli.errors as errors
from code42cli.logger import get_main_cli_logger

logger = get_main_cli_logger()


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
    store = FileEventCursorStore(profile.name) if args.incremental else None
    handlers = create_handlers(sdk, FileEventExtractor, output_logger, store)
    extractor = FileEventExtractor(sdk, handlers)
    if args.advanced_query:
        exit_if_advanced_query_used_with_other_search_args(args, FileEventFilterArguments())
        extractor.extract_advanced(args.advanced_query)
    else:
        verify_begin_date_requirements(args, store)
        if args.type:
            _verify_exposure_types(args.type)
        filters = _create_file_event_filters(args)
        extractor.extract(*filters)
    if handlers.TOTAL_EVENTS == 0 and not errors.ERRORED:
        logger.print_info(u"No results found.")


def _verify_exposure_types(exposure_types):
    if exposure_types is None:
        return
    options = list(ExposureTypeOptions())
    for exposure_type in exposure_types:
        if exposure_type not in options:
            logger.print_and_log_error(u"'{0}' is not a valid exposure type.".format(exposure_type))
            exit(1)


def _create_file_event_filters(args):
    filters = []
    event_timestamp_filter = create_time_range_filter(EventTimestamp, args.begin, args.end)
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


def _try_append_exposure_types_filter(filters, include_non_exposure_events, exposure_types):
    _exposure_filter = _create_exposure_type_filter(include_non_exposure_events, exposure_types)
    if _exposure_filter:
        filters.append(_exposure_filter)


def _create_exposure_type_filter(include_non_exposure_events, exposure_types):
    if include_non_exposure_events and exposure_types:
        logger.print_and_log_error(u"Cannot use exposure types with `--include-non-exposure`.")
        exit(1)
    if exposure_types:
        return ExposureType.is_in(exposure_types)
    if not include_non_exposure_events:
        return ExposureType.exists()
