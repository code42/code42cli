from pprint import pformat

import click
import py42.sdk.queries.fileevents.filters as f
from click import echo
from pandas import DataFrame
from pandas import json_normalize
from py42.exceptions import Py42InvalidPageTokenError
from py42.sdk.queries.fileevents.file_event_query import FileEventQuery
from py42.sdk.queries.fileevents.filters import InsertionTimestamp
from py42.sdk.queries.fileevents.filters.exposure_filter import ExposureType
from py42.sdk.queries.fileevents.filters.file_filter import FileCategory
from py42.sdk.queries.fileevents.filters.risk_filter import RiskIndicator
from py42.sdk.queries.fileevents.filters.risk_filter import RiskSeverity
from py42.sdk.queries.fileevents.v2 import FileEventQuery as FileEventQueryV2
from py42.sdk.queries.fileevents.v2 import filters as v2_filters

import code42cli.cmds.search.options as searchopt
import code42cli.options as opt
from code42cli.click_ext.groups import OrderedGroup
from code42cli.click_ext.options import incompatible_with
from code42cli.click_ext.types import MapChoice
from code42cli.cmds.search import SendToCommand
from code42cli.cmds.search.cursor_store import FileEventCursorStore
from code42cli.cmds.util import convert_to_or_query
from code42cli.cmds.util import create_time_range_filter
from code42cli.date_helper import convert_datetime_to_timestamp
from code42cli.date_helper import limit_date_range
from code42cli.enums import OutputFormat
from code42cli.errors import Code42CLIError
from code42cli.logger import get_main_cli_logger
from code42cli.options import column_option
from code42cli.options import format_option
from code42cli.options import sdk_options
from code42cli.output_formats import DataFrameOutputFormatter
from code42cli.output_formats import FileEventsOutputFormat
from code42cli.output_formats import FileEventsOutputFormatter
from code42cli.util import deprecation_warning
from code42cli.util import warn_interrupt

logger = get_main_cli_logger()
MAX_EVENT_PAGE_SIZE = 10000
DEPRECATION_TEXT = "(DEPRECATED): V1 file events are deprecated.  Update your profile with `code42 profile update --use-v2-file-events True` to use the new V2 file event data model."

SECURITY_DATA_KEYWORD = "file events"


def exposure_type_callback():
    def callback(ctx, param, arg):
        if arg:
            if ctx.obj.profile.use_v2_file_events == "True":
                raise Code42CLIError(
                    "Exposure type (--type/-t) filter is incompatible with V2 file events. Use the event action (--event-action) filter instead."
                )
            ctx.obj.search_filters.append(ExposureType.is_in(arg))
        return arg

    return callback


def event_action_callback():
    def callback(ctx, param, arg):
        if arg:
            if ctx.obj.profile.use_v2_file_events == "False":
                raise Code42CLIError(
                    "Event action (--event-action) filter is incompatible with V1 file events.  Upgrade your profile to use the V2 file event data model with `code42 profile update --use-v2-file-events True`"
                )
            ctx.obj.search_filters.append(v2_filters.event.Action.is_in(arg))
        return arg

    return callback


def get_all_events_callback():
    def callback(ctx, param, arg):
        if not arg:
            if ctx.obj.profile.use_v2_file_events == "True":
                ctx.obj.search_filters.append(
                    v2_filters.risk.Severity.not_eq(
                        v2_filters.risk.Severity.NO_RISK_INDICATED
                    )
                )
            else:
                ctx.obj.search_filters.append(ExposureType.exists())
            return arg

    return callback


file_events_format_option = click.option(
    "-f",
    "--format",
    type=click.Choice(FileEventsOutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to table format.",
    default=FileEventsOutputFormat.TABLE,
)
exposure_type_option = click.option(
    "-t",
    "--type",
    multiple=True,
    type=click.Choice(list(ExposureType.choices())),
    cls=searchopt.ExposureTypeIncompatible,
    callback=exposure_type_callback(),
    help="Limits events to those with given exposure types. Only compatible with V1 file events.",
)
event_action_option = click.option(
    "--event-action",
    multiple=True,
    type=click.Choice(list(v2_filters.event.Action.choices())),
    cls=searchopt.EventActionIncompatible,
    callback=event_action_callback(),
    help="Limits events to those with given event action. Only compatible with V2 file events.",
)
username_option = click.option(
    "--c42-username",
    multiple=True,
    callback=searchopt.is_in_filter(f.DeviceUsername, v2_filters.user.Email),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to endpoint events for these Code42 users.",
)
actor_option = click.option(
    "--actor",
    multiple=True,
    callback=searchopt.is_in_filter(f.Actor, v2_filters.user.Email),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to only those enacted by the cloud service user "
    "of the person who caused the event.",
)
md5_option = click.option(
    "--md5",
    multiple=True,
    callback=searchopt.is_in_filter(f.MD5, v2_filters.file.MD5),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file has one of these MD5 hashes.",
)
sha256_option = click.option(
    "--sha256",
    multiple=True,
    callback=searchopt.is_in_filter(f.SHA256, v2_filters.file.SHA256),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file has one of these SHA256 hashes.",
)
source_option = click.option(
    "--source",
    multiple=True,
    callback=searchopt.is_in_filter(f.Source, v2_filters.source.Name),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to only those from one of these sources. For example, Gmail, Box, or Endpoint.",
)
file_name_option = click.option(
    "--file-name",
    multiple=True,
    callback=searchopt.is_in_filter(f.FileName, v2_filters.file.Name),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file has one of these names.",
)
file_path_option = click.option(
    "--file-path",
    multiple=True,
    callback=searchopt.is_in_filter(f.FilePath, v2_filters.file.Directory),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file is located at one of these paths. Applies to endpoint file events only.",
)
file_category_option = click.option(
    "--file-category",
    multiple=True,
    type=MapChoice(
        choices=list(FileCategory.choices()),
        extras_map={
            "AUDIO": FileCategory.AUDIO,
            "DOCUMENT": FileCategory.DOCUMENT,
            "EXECUTABLE": FileCategory.EXECUTABLE,
            "IMAGE": FileCategory.IMAGE,
            "PDF": FileCategory.PDF,
            "PRESENTATION": FileCategory.PRESENTATION,
            "SCRIPT": FileCategory.SCRIPT,
            "SOURCE_CODE": FileCategory.SOURCE_CODE,
            "SPREADSHEET": FileCategory.SPREADSHEET,
            "VIDEO": FileCategory.VIDEO,
            "VIRTUAL_DISK_IMAGE": FileCategory.VIRTUAL_DISK_IMAGE,
            "ARCHIVE": FileCategory.ZIP,
            "ZIP": FileCategory.ZIP,
            "Zip": FileCategory.ZIP,
        },
    ),
    callback=searchopt.is_in_filter(f.FileCategory, v2_filters.file.Category),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to file events where the file can be classified by one of these categories.",
)
process_owner_option = click.option(
    "--process-owner",
    multiple=True,
    callback=searchopt.is_in_filter(f.ProcessOwner, v2_filters.process.Owner),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits exposure events by process owner, as reported by the device’s operating system. "
    "Applies only to `Printed` and `Browser or app read` events.",
)
tab_url_option = click.option(
    "--tab-url",
    multiple=True,
    callback=searchopt.is_in_filter(f.TabURL, v2_filters.destination.TabUrls),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to be exposure events with one of the specified destination tab URLs.",
)


include_non_exposure_option = click.option(
    "--include-non-exposure",
    is_flag=True,
    callback=get_all_events_callback(),
    cls=incompatible_with(["advanced_query", "type", "saved_search"]),
    help="Get all events including non-exposure events.",
)
risk_indicator_map = {
    "PUBLIC_CORPORATE_BOX": RiskIndicator.CloudDataExposures.PUBLIC_CORPORATE_BOX,
    "PUBLIC_CORPORATE_GOOGLE": RiskIndicator.CloudDataExposures.PUBLIC_CORPORATE_GOOGLE_DRIVE,
    "PUBLIC_CORPORATE_ONEDRIVE": RiskIndicator.CloudDataExposures.PUBLIC_CORPORATE_ONEDRIVE,
    "SENT_CORPORATE_GMAIL": RiskIndicator.CloudDataExposures.SENT_CORPORATE_GMAIL,
    "SHARED_CORPORATE_BOX": RiskIndicator.CloudDataExposures.SHARED_CORPORATE_BOX,
    "SHARED_CORPORATE_GOOGLE_DRIVE": RiskIndicator.CloudDataExposures.SHARED_CORPORATE_GOOGLE_DRIVE,
    "SHARED_CORPORATE_ONEDRIVE": RiskIndicator.CloudDataExposures.SHARED_CORPORATE_ONEDRIVE,
    "AMAZON_DRIVE": RiskIndicator.CloudStorageUploads.AMAZON_DRIVE,
    "BOX": RiskIndicator.CloudStorageUploads.BOX,
    "DROPBOX": RiskIndicator.CloudStorageUploads.DROPBOX,
    "GOOGLE_DRIVE": RiskIndicator.CloudStorageUploads.GOOGLE_DRIVE,
    "ICLOUD": RiskIndicator.CloudStorageUploads.ICLOUD,
    "MEGA": RiskIndicator.CloudStorageUploads.MEGA,
    "ONEDRIVE": RiskIndicator.CloudStorageUploads.ONEDRIVE,
    "ZOHO": RiskIndicator.CloudStorageUploads.ZOHO,
    "BITBUCKET": RiskIndicator.CodeRepositoryUploads.BITBUCKET,
    "GITHUB": RiskIndicator.CodeRepositoryUploads.GITHUB,
    "GITLAB": RiskIndicator.CodeRepositoryUploads.GITLAB,
    "SOURCEFORGE": RiskIndicator.CodeRepositoryUploads.SOURCEFORGE,
    "STASH": RiskIndicator.CodeRepositoryUploads.STASH,
    "163.COM": RiskIndicator.EmailServiceUploads.ONESIXTHREE_DOT_COM,
    "126.COM": RiskIndicator.EmailServiceUploads.ONETWOSIX_DOT_COM,
    "AOL": RiskIndicator.EmailServiceUploads.AOL,
    "COMCAST": RiskIndicator.EmailServiceUploads.COMCAST,
    "GMAIL": RiskIndicator.EmailServiceUploads.GMAIL,
    "ICLOUD_MAIL": RiskIndicator.EmailServiceUploads.ICLOUD,
    "MAIL.COM": RiskIndicator.EmailServiceUploads.MAIL_DOT_COM,
    "OUTLOOK": RiskIndicator.EmailServiceUploads.OUTLOOK,
    "PROTONMAIL": RiskIndicator.EmailServiceUploads.PROTONMAIL,
    "QQMAIL": RiskIndicator.EmailServiceUploads.QQMAIL,
    "SINA_MAIL": RiskIndicator.EmailServiceUploads.SINA_MAIL,
    "SOHU_MAIL": RiskIndicator.EmailServiceUploads.SOHU_MAIL,
    "YAHOO": RiskIndicator.EmailServiceUploads.YAHOO,
    "ZOHO_MAIL": RiskIndicator.EmailServiceUploads.ZOHO_MAIL,
    "AIRDROP": RiskIndicator.ExternalDevices.AIRDROP,
    "REMOVABLE_MEDIA": RiskIndicator.ExternalDevices.REMOVABLE_MEDIA,
    "AUDIO": RiskIndicator.FileCategories.AUDIO,
    "DOCUMENT": RiskIndicator.FileCategories.DOCUMENT,
    "EXECUTABLE": RiskIndicator.FileCategories.EXECUTABLE,
    "IMAGE": RiskIndicator.FileCategories.IMAGE,
    "PDF": RiskIndicator.FileCategories.PDF,
    "PRESENTATION": RiskIndicator.FileCategories.PRESENTATION,
    "SCRIPT": RiskIndicator.FileCategories.SCRIPT,
    "SOURCE_CODE": RiskIndicator.FileCategories.SOURCE_CODE,
    "SPREADSHEET": RiskIndicator.FileCategories.SPREADSHEET,
    "VIDEO": RiskIndicator.FileCategories.VIDEO,
    "VIRTUAL_DISK_IMAGE": RiskIndicator.FileCategories.VIRTUAL_DISK_IMAGE,
    "ZIP": RiskIndicator.FileCategories.ZIP,
    "FACEBOOK_MESSENGER": RiskIndicator.MessagingServiceUploads.FACEBOOK_MESSENGER,
    "MICROSOFT_TEAMS": RiskIndicator.MessagingServiceUploads.MICROSOFT_TEAMS,
    "SLACK": RiskIndicator.MessagingServiceUploads.SLACK,
    "WHATSAPP": RiskIndicator.MessagingServiceUploads.WHATSAPP,
    "OTHER": RiskIndicator.Other.OTHER,
    "UNKNOWN": RiskIndicator.Other.UNKNOWN,
    "FACEBOOK": RiskIndicator.SocialMediaUploads.FACEBOOK,
    "LINKEDIN": RiskIndicator.SocialMediaUploads.LINKEDIN,
    "REDDIT": RiskIndicator.SocialMediaUploads.REDDIT,
    "TWITTER": RiskIndicator.SocialMediaUploads.TWITTER,
    "FILE_MISMATCH": RiskIndicator.UserBehavior.FILE_MISMATCH,
    "OFF_HOURS": RiskIndicator.UserBehavior.OFF_HOURS,
    "REMOTE": RiskIndicator.UserBehavior.REMOTE,
    "FIRST_DESTINATION_USE": RiskIndicator.UserBehavior.FIRST_DESTINATION_USE,
    "RARE_DESTINATION_USE": RiskIndicator.UserBehavior.RARE_DESTINATION_USE,
}
risk_indicator_map_reversed = {v: k for k, v in risk_indicator_map.items()}


def risk_indicator_callback():
    def callback(ctx, param, arg):
        if arg:
            f_cls = f.RiskIndicator
            if ctx.obj.profile.use_v2_file_events == "True":
                f_cls = v2_filters.risk.Indicators
            mapped_args = tuple(risk_indicator_map[i] for i in arg)
            filter_func = searchopt.is_in_filter(f_cls)
            return filter_func(ctx, param, mapped_args)

    return callback


risk_indicator_option = click.option(
    "--risk-indicator",
    multiple=True,
    type=MapChoice(
        choices=list(risk_indicator_map.keys()),
        extras_map=risk_indicator_map_reversed,
    ),
    callback=risk_indicator_callback(),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to those classified by the given risk indicator categories.",
)
risk_severity_option = click.option(
    "--risk-severity",
    multiple=True,
    type=click.Choice(list(RiskSeverity.choices())),
    callback=searchopt.is_in_filter(f.RiskSeverity, v2_filters.risk.Severity),
    cls=searchopt.AdvancedQueryAndSavedSearchIncompatible,
    help="Limits events to those classified by the given risk severity.",
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


def _get_saved_search_option():
    def _get_saved_search_query(ctx, param, arg):
        if arg is None:
            return
        query = ctx.obj.sdk.securitydata.savedsearches.get_query(
            arg, use_v2=ctx.obj.profile.use_v2_file_events == "True"
        )
        return query

    return click.option(
        "--saved-search",
        help="Get events from a saved search filter with the given ID."
        "WARNING: Using a saved search is incompatible with other query-building arguments.",
        callback=_get_saved_search_query,
        cls=incompatible_with("advanced_query"),
    )


def search_options(f):
    f = column_option(f)
    f = checkpoint_option(f)
    f = advanced_query_option(f)
    f = searchopt.or_query_option(f)
    f = end_option(f)
    f = begin_option(f)
    return f


def file_event_options(f):
    f = exposure_type_option(f)
    f = event_action_option(f)
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
    f = risk_indicator_option(f)
    f = risk_severity_option(f)
    f = _get_saved_search_option()(f)
    return f


@click.group(cls=OrderedGroup)
@sdk_options(hidden=True)
def security_data(state):
    """Get and send file event data."""
    # store cursor getter on the group state so shared --begin option can use it in validation
    state.cursor_getter = _get_file_event_cursor_store


@security_data.command()
@click.argument("checkpoint-name")
@sdk_options()
def clear_checkpoint(state, checkpoint_name):
    """Remove the saved file event checkpoint from `--use-checkpoint/-c` mode."""
    _get_file_event_cursor_store(state.profile.name).delete(checkpoint_name)


@security_data.command()
@file_event_options
@search_options
@sdk_options()
@column_option
@searchopt.include_all_option
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
    columns,
    include_all,
    **kwargs,
):
    """Search for file events."""

    if state.profile.use_v2_file_events != "True":
        deprecation_warning(DEPRECATION_TEXT)

    if format == FileEventsOutputFormat.CEF and columns:
        raise click.BadOptionUsage(
            "columns", "--columns option can't be used with CEF format."
        )

    # cef format unsupported for v2 file events
    if (
        format == FileEventsOutputFormat.CEF
        and state.profile.use_v2_file_events == "True"
    ):
        raise click.BadOptionUsage(
            "format", "--format CEF is unsupported for v2 file events."
        )

    # set default table columns
    if format == OutputFormat.TABLE:
        if not columns and not include_all:
            if state.profile.use_v2_file_events == "True":
                columns = [
                    "@timestamp",
                    "file.name",
                    "file.directory",
                    "event.action",
                    "file.category",
                    "file.sizeInBytes",
                    "file.owner",
                    "file.hash.md5",
                    "file.hash.sha256",
                    "risk.indicators",
                    "risk.severity",
                ]
            else:
                columns = [
                    "fileName",
                    "filePath",
                    "eventType",
                    "eventTimestamp",
                    "fileCategory",
                    "fileSize",
                    "fileOwner",
                    "md5Checksum",
                    "sha256Checksum",
                    "riskIndicators",
                    "riskSeverity",
                ]

    if use_checkpoint:
        cursor = _get_file_event_cursor_store(state.profile.name)
        checkpoint = _handle_timestamp_checkpoint(cursor.get(use_checkpoint), state)

        if state.profile.use_v2_file_events == "True":

            def checkpoint_func(event):
                cursor.replace(use_checkpoint, event["event.id"])

        else:

            def checkpoint_func(event):
                cursor.replace(use_checkpoint, event["eventId"])

    else:
        checkpoint = checkpoint_func = None

    query = _construct_query(state, begin, end, saved_search, advanced_query, or_query)
    flatten = format in (OutputFormat.TABLE, OutputFormat.CSV)
    dfs = _get_all_file_events(state, query, checkpoint, flatten)
    formatter = FileEventsOutputFormatter(format, checkpoint_func=checkpoint_func)
    # sending to pager when checkpointing can be inaccurate due to pager buffering, so disallow pager
    force_no_pager = use_checkpoint
    formatter.echo_formatted_dataframes(
        dfs, columns=columns, force_no_pager=force_no_pager
    )


@security_data.command(cls=SendToCommand)
@file_event_options
@search_options
@sdk_options()
@searchopt.server_options
@searchopt.send_to_format_options
def send_to(
    state,
    begin,
    end,
    advanced_query,
    use_checkpoint,
    saved_search,
    or_query,
    columns,
    **kwargs,
):
    """Send events to the given server address.

    HOSTNAME format: address:port where port is optional and defaults to 514.
    """
    if state.profile.use_v2_file_events != "True":
        deprecation_warning(DEPRECATION_TEXT)

    if use_checkpoint:
        cursor = _get_file_event_cursor_store(state.profile.name)
        checkpoint = _handle_timestamp_checkpoint(cursor.get(use_checkpoint), state)

        if state.profile.use_v2_file_events == "True":

            def checkpoint_func(event):
                cursor.replace(use_checkpoint, event["event.id"])

        else:

            def checkpoint_func(event):
                cursor.replace(use_checkpoint, event["eventId"])

    else:
        checkpoint = checkpoint_func = None

    query = _construct_query(state, begin, end, saved_search, advanced_query, or_query)
    dfs = _get_all_file_events(state, query, checkpoint)
    formatter = FileEventsOutputFormatter(None, checkpoint_func=checkpoint_func)

    with warn_interrupt():
        event = None
        for event in formatter.iter_rows(dfs, columns=columns):
            state.logger.info(event)
        if event is None:  # generator was empty
            click.echo("No results found.")


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
    if state.profile.use_v2_file_events != "True":
        deprecation_warning(DEPRECATION_TEXT)

    formatter = DataFrameOutputFormatter(format)
    response = state.sdk.securitydata.savedsearches.get(
        use_v2=state.profile.use_v2_file_events == "True"
    )
    saved_searches_df = DataFrame(response["searches"])
    formatter.echo_formatted_dataframes(
        saved_searches_df, columns=["name", "id", "notes"]
    )


@saved_search.command()
@click.argument("search-id")
@sdk_options()
def show(state, search_id):
    """Get the details of a saved search."""
    if state.profile.use_v2_file_events != "True":
        deprecation_warning(DEPRECATION_TEXT)

    response = state.sdk.securitydata.savedsearches.get_by_id(
        search_id, use_v2=state.profile.use_v2_file_events == "True"
    )
    echo(pformat(response["searches"]))


def _get_file_event_cursor_store(profile_name):
    return FileEventCursorStore(profile_name)


def _construct_query(state, begin, end, saved_search, advanced_query, or_query):

    if advanced_query:
        state.search_filters = advanced_query
    elif saved_search:
        state.search_filters = saved_search._filter_group_list
    else:
        if begin or end:
            timestamp_class = (
                v2_filters.timestamp.Timestamp
                if state.profile.use_v2_file_events == "True"
                else f.EventTimestamp
            )
            state.search_filters.append(
                create_time_range_filter(timestamp_class, begin, end)
            )
    if or_query:
        state.search_filters = convert_to_or_query(state.search_filters)

    if not state.search_filters:
        # if a checkpoint and _only_ --include-non-exposure is passed, the filter list will be empty, which isn't a
        # valid query, so in that case we want to fallback to retrieving all events. The checkpoint will
        # still cause the query results to only contain events after the checkpointed event.
        severity_filter = (
            v2_filters.risk.Severity.exists()
            if state.profile.use_v2_file_events == "True"
            else RiskSeverity.exists()
        )
        state.search_filters.append(severity_filter)

    # construct a v2 model query if profile setting enabled
    if state.profile.use_v2_file_events == "True":
        query = FileEventQueryV2(*state.search_filters)
        query.sort_key = "@timestamp"
    else:
        query = FileEventQuery(*state.search_filters)
        query.sort_key = "insertionTimestamp"
    query.page_size = MAX_EVENT_PAGE_SIZE
    query.sort_direction = "asc"
    return query


def _get_all_file_events(state, query, checkpoint="", flatten=False):
    if checkpoint is None:
        checkpoint = ""
    try:
        response = state.sdk.securitydata.search_all_file_events(
            query, page_token=checkpoint
        )
    except Py42InvalidPageTokenError:
        response = state.sdk.securitydata.search_all_file_events(query)

    data = response["fileEvents"]
    if data and flatten:
        data = json_normalize(data)
    yield DataFrame(data)

    while response["nextPgToken"]:
        response = state.sdk.securitydata.search_all_file_events(
            query, page_token=response["nextPgToken"]
        )
        data = response["fileEvents"]
        if data and flatten:
            data = json_normalize(data)
        yield DataFrame(data)


def _handle_timestamp_checkpoint(checkpoint, state):
    try:
        checkpoint = float(checkpoint)
        if state.profile.use_v2_file_events == "True":
            state.search_filters.append(
                v2_filters.timestamp.Timestamp.on_or_after(checkpoint)
            )
        else:
            state.search_filters.append(InsertionTimestamp.on_or_after(checkpoint))
        return None
    except (ValueError, TypeError):
        return checkpoint
