from pprint import pformat

import click
import py42.sdk.queries.fileevents.filters as f
from c42eventextractor.extractors import FileEventExtractor
from click import echo

import code42cli.cmds.search.enums as enum
import code42cli.cmds.search.extraction as ext
import code42cli.cmds.search.options as searchopt
import code42cli.errors as errors
from code42cli.cmds.search import logger_factory
from code42cli.cmds.search.cursor_store import FileEventCursorStore
from code42cli.logger import get_main_cli_logger
from code42cli.options import incompatible_with
from code42cli.options import OrderedGroup
from code42cli.options import sdk_options
from code42cli.output_formats import format_option as format_output


logger = get_main_cli_logger()

search_options = searchopt.create_search_options("file events")

format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(enum.OutputFormat()),
    default=enum.OutputFormat.JSON,
    help="The format used for outputting file events.",
)
exposure_type_option = click.option(
    "-t",
    "--type",
    multiple=True,
    type=click.Choice(list(enum.ExposureType())),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    callback=searchopt.is_in_filter(f.ExposureType),
    help="Limits events to those with given exposure types.",
)
username_option = click.option(
    "--c42-username",
    multiple=True,
    callback=searchopt.is_in_filter(f.DeviceUsername),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to endpoint events for these users.",
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
    help="Limits events to only those from one of these sources. Example=Gmail.",
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
    help="Limits events to file events where the file is located at one of these paths.",
)
process_owner_option = click.option(
    "--process-owner",
    multiple=True,
    callback=searchopt.is_in_filter(f.ProcessOwner),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to exposure events where one of these users owns "
    "the process behind the exposure.",
)
tab_url_option = click.option(
    "--tab-url",
    multiple=True,
    callback=searchopt.is_in_filter(f.TabURL),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to be exposure events with one of these destination tab URLs.",
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
    f = saved_search_option(f)
    return f


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def security_data(state):
    """Tools for getting security related data, such as file events."""
    # store cursor getter on the group state so shared --begin option can use it in validation
    state.cursor_getter = _get_file_event_cursor_store


@security_data.command()
@click.argument("checkpoint-name")
@sdk_options()
def clear_checkpoint(state, checkpoint_name):
    """Remove the saved file event checkpoint from '--use-checkpoint/-c' mode."""
    _get_file_event_cursor_store(state.profile.name).delete(checkpoint_name)


@security_data.command()
@file_event_options
@search_options
@click.option(
    "--or-query", is_flag=True, cls=searchopt.AdvancedQueryAndSavedSearchIncompatible
)
@sdk_options()
def search(
    state,
    format,
    begin,
    end,
    advanced_query,
    use_checkpoint,
    saved_search,
    or_query,
    **kwargs
):
    """Search for file events."""
    output_logger = logger_factory.get_logger_for_stdout(format)
    cursor = (
        _get_file_event_cursor_store(state.profile.name) if use_checkpoint else None
    )
    handlers = ext.create_handlers(
        state.sdk, FileEventExtractor, output_logger, cursor, use_checkpoint
    )
    extractor = _get_file_event_extractor(state.sdk, handlers)
    extractor.use_or_query = or_query
    extractor.or_query_exempt_filters.append(f.ExposureType.exists())
    if advanced_query:
        extractor.extract_advanced(advanced_query)
    elif saved_search:
        extractor.extract(*saved_search._filter_group_list)
    else:
        if begin or end:
            state.search_filters.append(
                ext.create_time_range_filter(f.EventTimestamp, begin, end)
            )
        extractor.extract(*state.search_filters)
    if handlers.TOTAL_EVENTS == 0 and not errors.ERRORED:
        echo("No results found.")


@security_data.group(cls=OrderedGroup)
@sdk_options()
def saved_search(state):
    pass


@saved_search.command("list")
@format_output
@sdk_options()
def _list(state, format=None):
    """List available saved searches."""
    response = state.sdk.securitydata.savedsearches.get()
    header = {"name": "Name", "id": "Id"}
    result = response["searches"]
    if result:
        output = format(result, header)
        echo(output)


@saved_search.command()
@click.argument("search-id")
@sdk_options()
def show(state, search_id):
    """Get the details of a saved search."""
    response = state.sdk.securitydata.savedsearches.get_by_id(search_id)
    echo(pformat(response["searches"]))


def _get_file_event_extractor(sdk, handlers):
    return FileEventExtractor(sdk, handlers)


def _get_file_event_cursor_store(profile_name):
    return FileEventCursorStore(profile_name)
