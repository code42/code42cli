import click

from code42cli.options import global_options, incompatible_with
from code42cli.cmds.search_shared import logger_factory
from py42.sdk.queries.fileevents.filters import *
from c42eventextractor.extractors import FileEventExtractor

from code42cli.cmds.search_shared.options import (
    create_search_options,
    AdvancedQueryIncompatible,
    is_in_filter,
    exists_filter,
    output_file_arg,
    server_options,
)
from code42cli.cmds.search_shared.enums import (
    OutputFormat,
    ExposureType as ExposureTypeOptions,
)
from code42cli.cmds.search_shared.cursor_store import FileEventCursorStore
from code42cli.cmds.search_shared.extraction import (
    create_handlers,
    create_time_range_filter,
)
import code42cli.errors as errors
from code42cli.logger import get_main_cli_logger

logger = get_main_cli_logger()

search_options = create_search_options("file events")

format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(OutputFormat()),
    default=OutputFormat.JSON,
    help="The format used for outputting file events.",
)
exposure_type_option = click.option(
    "-t",
    "--type",
    multiple=True,
    type=click.Choice(list(ExposureTypeOptions())),
    cls=AdvancedQueryIncompatible,
    callback=is_in_filter(ExposureType),
    help="Limits events to those with given exposure types.",
)
username_option = click.option(
    "--c42-username",
    multiple=True,
    callback=is_in_filter(DeviceUsername),
    cls=AdvancedQueryIncompatible,
    help="Limits events to endpoint events for these users.",
)
actor_option = click.option(
    "--actor",
    multiple=True,
    callback=is_in_filter(Actor),
    cls=AdvancedQueryIncompatible,
    help="Limits events to only those enacted by the cloud service user "
    "of the person who caused the event.",
)
md5_option = click.option(
    "--md5",
    multiple=True,
    callback=is_in_filter(MD5),
    cls=AdvancedQueryIncompatible,
    help="Limits events to file events where the file has one of these MD5 hashes.",
)
sha256_option = click.option(
    "--sha256",
    multiple=True,
    callback=is_in_filter(SHA256),
    cls=AdvancedQueryIncompatible,
    help="Limits events to file events where the file has one of these SHA256 hashes.",
)
source_option = click.option(
    "--source",
    multiple=True,
    callback=is_in_filter(Source),
    cls=AdvancedQueryIncompatible,
    help="Limits events to only those from one of these sources. Example=Gmail.",
)
file_name_option = click.option(
    "--file-name",
    multiple=True,
    callback=is_in_filter(FileName),
    cls=AdvancedQueryIncompatible,
    help="Limits events to file events where the file has one of these names.",
)
file_path_option = click.option(
    "--file-path",
    multiple=True,
    callback=is_in_filter(FilePath),
    cls=AdvancedQueryIncompatible,
    help="Limits events to file events where the file is located at one of these paths.",
)
process_owner_option = click.option(
    "--process-owner",
    multiple=True,
    callback=is_in_filter(ProcessOwner),
    cls=AdvancedQueryIncompatible,
    help="Limits events to exposure events where one of these users owns "
    "the process behind the exposure.",
)
tab_url_option = click.option(
    "--tab-url",
    multiple=True,
    callback=is_in_filter(TabURL),
    cls=AdvancedQueryIncompatible,
    help="Limits events to be exposure events with one of these destination tab URLs.",
)
include_non_exposure_option = click.option(
    "--include-non-exposure",
    is_flag=True,
    callback=exists_filter(ExposureType),
    cls=incompatible_with(["advanced_query", "type"]),
    help="Get all events including non-exposure events.",
)


def file_event_options(f):
    f = exposure_type_option(f)
    f = username_option(f)
    f = actor_option(f)
    f = md5_option(f)
    f = sha256_option(f)
    f = source_option(f)
    f = file_name_option(f)
    f = file_path_option(f)
    f = process_owner_option(f)
    f = tab_url_option(f)
    f = include_non_exposure_option(f)
    f = format_option(f)
    return f


@click.group()
@global_options
def security_data(state):
    """Tools for getting security related data, such as file events."""
    state.cursor = FileEventCursorStore(state.profile.name)


@security_data.command()
@global_options
def clear_checkpoint(state):
    """Remove the saved file event checkpoint from 'incremental' (-i) mode."""
    state.cursor.replace_stored_cursor_timestamp(None)


@security_data.command("print")
@file_event_options
@search_options
@global_options
def _print(state, format, begin, end, advanced_query, incremental, **kwargs):
    """Print file events to stdout."""
    output_logger = logger_factory.get_logger_for_stdout(format)
    _extract(
        state.sdk,
        state.profile,
        state.search_filters,
        begin,
        end,
        advanced_query,
        incremental,
        output_logger,
    )


@security_data.command()
@output_file_arg
@file_event_options
@search_options
@global_options
def write_to(state, format, output_file, begin, end, advanced_query, incremental, **kwargs):
    """Write file events to the file with the given name."""
    output_logger = logger_factory.get_logger_for_file(output_file, format)
    _extract(
        state.sdk,
        state.profile,
        state.search_filters,
        begin,
        end,
        advanced_query,
        incremental,
        output_logger,
    )


@security_data.command()
@server_options
@file_event_options
@search_options
@global_options
def send_to(state, format, hostname, protocol, begin, end, advanced_query, incremental, **kwargs):
    """Send file events to the given server address."""
    output_logger = logger_factory.get_logger_for_server(hostname, protocol, format)
    _extract(
        state.sdk,
        state.profile,
        state.search_filters,
        begin,
        end,
        advanced_query,
        incremental,
        output_logger,
    )


def _extract(sdk, profile, filter_list, begin, end, advanced_query, incremental, output_logger):
    store = FileEventCursorStore(profile.name) if incremental else None
    handlers = create_handlers(sdk, FileEventExtractor, output_logger, store)
    extractor = FileEventExtractor(sdk, handlers)
    if advanced_query:
        extractor.extract_advanced(advanced_query)
    else:
        if begin or end:
            filter_list.append(create_time_range_filter(EventTimestamp, begin, end))
        extractor.extract(*filter_list)
    if handlers.TOTAL_EVENTS == 0 and not errors.ERRORED:
        logger.print_info(u"No results found.")
