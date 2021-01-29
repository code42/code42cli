from _collections import OrderedDict
from pprint import pformat

import click
import py42.sdk.queries.fileevents.filters as f
from c42eventextractor.extractors import FileEventExtractor
from click import echo
from py42.sdk.queries.fileevents.filters.exposure_filter import ExposureType
from py42.sdk.queries.fileevents.filters.file_filter import FileCategory

import code42cli.cmds.search.enums as enum
import code42cli.cmds.search.extraction as ext
import code42cli.cmds.search.options as searchopt
import code42cli.errors as errors
import code42cli.options as opt
from code42cli.click_ext.groups import OrderedGroup
from code42cli.click_ext.options import incompatible_with
from code42cli.cmds.search.cursor_store import FileEventCursorStore
from code42cli.cmds.search.extraction import handle_no_events
from code42cli.cmds.securitydata_output_formats import FileEventsOutputFormatter
from code42cli.date_helper import convert_datetime_to_timestamp
from code42cli.date_helper import limit_date_range
from code42cli.logger import get_logger_for_server
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.options import send_to_format_options
from code42cli.options import server_options
from code42cli.output_formats import OutputFormatter

SECURITY_DATA_KEYWORD = "file events"
_HEADER_KEYS_MAP = OrderedDict()
_HEADER_KEYS_MAP["name"] = "Name"
_HEADER_KEYS_MAP["id"] = "Id"

SEARCH_DEFAULT_HEADER = OrderedDict()
SEARCH_DEFAULT_HEADER["fileName"] = "FileName"
SEARCH_DEFAULT_HEADER["filePath"] = "FilePath"
SEARCH_DEFAULT_HEADER["eventType"] = "Type"
SEARCH_DEFAULT_HEADER["eventTimestamp"] = "EventTimestamp"
SEARCH_DEFAULT_HEADER["fileCategory"] = "FileCategory"
SEARCH_DEFAULT_HEADER["fileSize"] = "FileSize"
SEARCH_DEFAULT_HEADER["fileOwner"] = "FileOwner"
SEARCH_DEFAULT_HEADER["md5Checksum"] = "MD5Checksum"
SEARCH_DEFAULT_HEADER["sha256Checksum"] = "SHA256Checksum"


file_events_format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(enum.FileEventsOutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to table format.",
    default=enum.FileEventsOutputFormat.TABLE,
)
exposure_type_option = click.option(
    "-t",
    "--type",
    multiple=True,
    type=click.Choice(list(ExposureType.choices())),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.ExposureType),
    help="Limits events to those with given exposure types.",
)
username_option = click.option(
    "--c42-username",
    multiple=True,
    callback=searchopt.is_in_filter(f.DeviceUsername),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to endpoint events for these Code42 users.",
)
actor_option = click.option(
    "--actor",
    multiple=True,
    callback=searchopt.is_in_filter(f.Actor),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to only those enacted by the cloud service user "
    "of the person who caused the event.",
)
md5_option = click.option(
    "--md5",
    multiple=True,
    callback=searchopt.is_in_filter(f.MD5),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file has one of these MD5 hashes.",
)
sha256_option = click.option(
    "--sha256",
    multiple=True,
    callback=searchopt.is_in_filter(f.SHA256),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file has one of these SHA256 hashes.",
)
source_option = click.option(
    "--source",
    multiple=True,
    callback=searchopt.is_in_filter(f.Source),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to only those from one of these sources. For example, Gmail, Box, or Endpoint.",
)
file_name_option = click.option(
    "--file-name",
    multiple=True,
    callback=searchopt.is_in_filter(f.FileName),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file has one of these names.",
)
file_path_option = click.option(
    "--file-path",
    multiple=True,
    callback=searchopt.is_in_filter(f.FilePath),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file is located at one of these paths. Applies to endpoint file events only.",
)
file_category_option = click.option(
    "--file-category",
    multiple=True,
    type=click.Choice(list(FileCategory.choices())),
    callback=searchopt.is_in_filter(f.FileCategory),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file can be classified by one of these categories.",
)
process_owner_option = click.option(
    "--process-owner",
    multiple=True,
    callback=searchopt.is_in_filter(f.ProcessOwner),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits exposure events by process owner, as reported by the device’s operating system. "
    "Applies only to `Printed` and `Browser or app read` events.",
)
tab_url_option = click.option(
    "--tab-url",
    multiple=True,
    callback=searchopt.is_in_filter(f.TabURL),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to be exposure events with one of the specified destination tab URLs.",
)
include_non_exposure_option = click.option(
    "--include-non-exposure",
    is_flag=True,
    callback=searchopt.exists_filter(f.ExposureType),
    cls=incompatible_with(["advanced_query", "type", "saved_search"]),
    help="Get all events including non-exposure events.",
)


def _get_saved_search_query(ctx, param, arg):
    if arg is None:
        return
    query = ctx.obj.sdk.securitydata.savedsearches.get_query(arg)
    return query


saved_search_option = click.option(
    "--saved-search",
    help="Get events from a saved search filter with the given ID.",
    callback=_get_saved_search_query,
    cls=incompatible_with("advanced_query"),
)

begin_option = opt.begin_option(
    SECURITY_DATA_KEYWORD,
    callback=lambda ctx, param, arg: convert_datetime_to_timestamp(
        limit_date_range(arg, max_days_back=90)
    ),
)
end_option = opt.end_option(SECURITY_DATA_KEYWORD)
checkpoint_option = opt.checkpoint_option(
    SECURITY_DATA_KEYWORD, cls=searchopt.AdvancedQueryAndSavedSearchIncompatible
)
advanced_query_option = searchopt.advanced_query_option(SECURITY_DATA_KEYWORD)


def search_options(f):
    f = checkpoint_option(f)
    f = advanced_query_option(f)
    f = end_option(f)
    f = begin_option(f)
    return f


def file_event_options(f):
    f = exposure_type_option(f)
    f = username_option(f)
    f = actor_option(f)
    f = md5_option(f)
    f = sha256_option(f)
    f = source_option(f)
    f = file_name_option(f)
    f = file_path_option(f)
    f = file_category_option(f)
    f = process_owner_option(f)
    f = tab_url_option(f)
    f = include_non_exposure_option(f)
    f = saved_search_option(f)
    return f


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def security_data(state):
    """Tools for getting file event data."""
    # store cursor getter on the group state so shared --begin option can use it in validation
    state.cursor_getter = _get_file_event_cursor_store


@security_data.command()
@click.argument("checkpoint-name")
@sdk_options()
def clear_checkpoint(state, checkpoint_name):
    """Remove the saved file event checkpoint from `--use-checkpoint/-c` mode."""
    _get_file_event_cursor_store(state.profile.name).delete(checkpoint_name)


def _call_extractor(
    state, handlers, begin, end, or_query, advanced_query, saved_search, **kwargs
):
    if advanced_query:
        state.search_filters = advanced_query
    extractor = _get_file_event_extractor(state.sdk, handlers)
    extractor.use_or_query = or_query
    extractor.or_query_exempt_filters.append(f.ExposureType.exists())
    if saved_search:
        extractor.extract(*saved_search._filter_group_list)
    else:
        if begin or end:
            state.search_filters.append(
                ext.create_time_range_filter(f.EventTimestamp, begin, end)
            )
        extractor.extract(*state.search_filters)


@security_data.command()
@file_event_options
@search_options
@click.option(
    "--or-query", is_flag=True, cls=searchopt.AdvancedQueryAndSavedSearchIncompatible
)
@sdk_options()
@click.option(
    "--include-all",
    default=False,
    is_flag=True,
    help="Display simple properties of the primary level of the nested response.",
)
@file_events_format_option
def search(
    state,
    format,
    begin,
    end,
    advanced_query,
    use_checkpoint,
    saved_search,
    or_query,
    include_all,
    **kwargs,
):
    """Search for file events."""
    output_header = ext.try_get_default_header(
        include_all, SEARCH_DEFAULT_HEADER, format
    )

    formatter = FileEventsOutputFormatter(format, output_header)
    cursor = (
        _get_file_event_cursor_store(state.profile.name) if use_checkpoint else None
    )
    handlers = ext.create_handlers(
        state.sdk,
        FileEventExtractor,
        cursor,
        use_checkpoint,
        formatter=formatter,
        force_pager=include_all,
    )
    _call_extractor(
        state, handlers, begin, end, or_query, advanced_query, saved_search, **kwargs
    )

    handle_no_events(not handlers.TOTAL_EVENTS and not errors.ERRORED)


@security_data.group(cls=OrderedGroup)
@sdk_options()
def saved_search(state):
    """Search for file events using saved searches."""
    pass


@saved_search.command("list")
@format_option
@sdk_options()
def _list(state, format=None):
    """List available saved searches."""
    formatter = OutputFormatter(format, _HEADER_KEYS_MAP)
    response = state.sdk.securitydata.savedsearches.get()
    saved_searches = response["searches"]
    if saved_searches:
        formatter.echo_formatted_list(saved_searches)


@saved_search.command()
@click.argument("search-id")
@sdk_options()
def show(state, search_id):
    """Get the details of a saved search."""
    response = state.sdk.securitydata.savedsearches.get_by_id(search_id)
    echo(pformat(response["searches"]))


@security_data.command()
@file_event_options
@search_options
@click.option(
    "--or-query",
    is_flag=True,
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Combine query filter options with 'OR' logic instead of the default 'AND'.",
)
@sdk_options()
@server_options
@click.option(
    "--include-all",
    default=False,
    is_flag=True,
    help="Display simple properties of the primary level of the nested response.",
)
@send_to_format_options
def send_to(
    state,
    format,
    hostname,
    protocol,
    begin,
    end,
    advanced_query,
    use_checkpoint,
    saved_search,
    or_query,
    **kwargs,
):
    """Send events to the given server address.

    HOSTNAME format: address:port where port is optional and defaults to 514.
    """
    logger = get_logger_for_server(hostname, protocol, format)
    cursor = (
        _get_file_event_cursor_store(state.profile.name) if use_checkpoint else None
    )
    handlers = ext.create_send_to_handlers(
        state.sdk, FileEventExtractor, cursor, use_checkpoint, logger
    )
    _call_extractor(
        state, handlers, begin, end, or_query, advanced_query, saved_search, **kwargs
    )
    handle_no_events(not handlers.TOTAL_EVENTS and not errors.ERRORED)


def _get_file_event_extractor(sdk, handlers):
    return FileEventExtractor(sdk, handlers)


def _get_file_event_cursor_store(profile_name):
    return FileEventCursorStore(profile_name)
