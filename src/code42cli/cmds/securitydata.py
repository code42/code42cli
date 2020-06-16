import click

from code42cli.sdk_client import sdk_options
from code42cli.cmds.search_shared import logger_factory, args
from code42cli.date_helper import parse_min_timestamp, parse_max_timestamp
from py42.sdk.queries.fileevents.filters import *
from c42eventextractor.extractors import FileEventExtractor

from code42cli.cmds.search_shared.enums import ExposureType as ExposureTypeOptions
from code42cli.cmds.search_shared.cursor_store import FileEventCursorStore
from code42cli.cmds.search_shared.extraction import (
    verify_begin_date_requirements,
    create_handlers,
    create_time_range_filter,
)


@click.group()
@sdk_options
def security_data(sdk):
    pass


def is_in_filter(filter_cls):
    def f(ctx, arg):
        if arg is not None:
            ctx.obj.search_filters.append(filter_cls.is_in(arg))
            return arg

    return f


def exists_filter(filter_cls):
    def f(ctx, arg):
        if arg:
            ctx.obj.search_filters.append(filter_cls.exists())
            return arg

    return f


def incompatible_with(incompatible_opts):
    """Returns a custom click.Option subclass that is incompatible with the option names 
    provided.
    """
    if isinstance(incompatible_opts, str):
        incompatible_opts = [incompatible_opts]

    class IncompatibleOption(click.Option):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def handle_parse_result(self, ctx, opts, args):
            found_incompatible = ", ".join(
                ["--{}".format(opt) for opt in opts if opt in incompatible_opts]
            )
            if self.name in opts and found_incompatible:
                raise click.BadOptionUsage(
                    option_name="incompatible_opt",
                    message="Cannot use option '--{}' with: {}".format(
                        self.name, found_incompatible
                    ),
                )
            return super().handle_parse_result(ctx, opts, args)

    return IncompatibleOption


AdvancedQueryIncompatible = incompatible_with("advanced_query")


@security_data.command("print")
@sdk_options
@click.option(
    "-f",
    "--format",
    type=click.Choice(["JSON", "RAW-JSON", "CEF"]),
    default="JSON",
    callback=lambda ctx, value: logger_factory.get_logger_for_stdout(value),
)
@click.option("-b", "--begin", callback=parse_min_timestamp, cls=AdvancedQueryIncompatible)
@click.option("-e", "--end", callback=parse_max_timestamp, cls=AdvancedQueryIncompatible)
@click.option("-i", "--incremental", is_flag=True)
@click.option("--advanced-query")
@click.option(
    "-t",
    "--type",
    multiple=True,
    type=click.Choice(list(ExposureTypeOptions())),
    cls=AdvancedQueryIncompatible,
    callback=is_in_filter(ExposureType),
)
@click.option(
    "--c42-username", callback=is_in_filter(DeviceUsername), cls=AdvancedQueryIncompatible
)
@click.option("--actor", callback=is_in_filter(Actor), cls=AdvancedQueryIncompatible)
@click.option("--md5", callback=is_in_filter(MD5), cls=AdvancedQueryIncompatible)
@click.option("--sha256", callback=is_in_filter(SHA256), cls=AdvancedQueryIncompatible)
@click.option("--source", callback=is_in_filter(Source), cls=AdvancedQueryIncompatible)
@click.option("--file-name", callback=is_in_filter(FileName), cls=AdvancedQueryIncompatible)
@click.option("--file-path", callback=is_in_filter(FilePath), cls=AdvancedQueryIncompatible)
@click.option("--process-owner", callback=is_in_filter(ProcessOwner), cls=AdvancedQueryIncompatible)
@click.option("--tab-url", callback=is_in_filter(TabURL), cls=AdvancedQueryIncompatible)
@click.option(
    "--include-non-exposure",
    is_flag=True,
    callback=exists_filter(ExposureType),
    cls=incompatible_with(["advanced_query", "type"]),
)
def _print(
    sdk,
    begin,
    end,
    format,
    advanced_query,
    type,
    c42_username,
    actor,
    md5,
    sha256,
    source,
    file_name,
    file_path,
    process_owner,
    tab_url,
    include_non_exposure,
    incremental,
):
    """Print file events to stdout."""
    filters = sdk.search_filters
    store = FileEventCursorStore(sdk.profile.name) if incremental else None
    verify_begin_date_requirements(begin, incremental, store)
    if begin or end:
        filters.append(create_time_range_filter(EventTimestamp, begin, end))
    handlers = create_handlers(sdk, FileEventExtractor, format, store)
    extractor = FileEventExtractor(sdk, handlers)
    extractor.extract(*filters)
