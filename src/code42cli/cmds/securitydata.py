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
import code42cli.errors as errors
from code42cli.logger import get_main_cli_logger

logger = get_main_cli_logger()


@click.group()
@sdk_options
def security_data(sdk):
    pass


def is_in_filter(filter_cls):
    def f(ctx, arg):
        if arg:
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
    "--c42-username",
    multiple=True,
    callback=is_in_filter(DeviceUsername),
    cls=AdvancedQueryIncompatible,
)
@click.option("--actor", multiple=True, callback=is_in_filter(Actor), cls=AdvancedQueryIncompatible)
@click.option("--md5", multiple=True, callback=is_in_filter(MD5), cls=AdvancedQueryIncompatible)
@click.option(
    "--sha256", multiple=True, callback=is_in_filter(SHA256), cls=AdvancedQueryIncompatible
)
@click.option(
    "--source", multiple=True, callback=is_in_filter(Source), cls=AdvancedQueryIncompatible
)
@click.option(
    "--file-name", multiple=True, callback=is_in_filter(FileName), cls=AdvancedQueryIncompatible
)
@click.option(
    "--file-path", multiple=True, callback=is_in_filter(FilePath), cls=AdvancedQueryIncompatible
)
@click.option(
    "--process-owner",
    multiple=True,
    callback=is_in_filter(ProcessOwner),
    cls=AdvancedQueryIncompatible,
)
@click.option(
    "--tab-url", multiple=True, callback=is_in_filter(TabURL), cls=AdvancedQueryIncompatible
)
@click.option(
    "--include-non-exposure",
    is_flag=True,
    callback=exists_filter(ExposureType),
    cls=incompatible_with(["advanced_query", "type"]),
)
def _print(sdk, begin, end, format, advanced_query, incremental, **kwargs):
    """Print file events to stdout."""
    store = FileEventCursorStore(sdk.profile.name) if incremental else None
    handlers = create_handlers(sdk, FileEventExtractor, format, store)
    extractor = FileEventExtractor(sdk, handlers)
    if advanced_query:
        extractor.extract_advanced(advanced_query)
    else:
        verify_begin_date_requirements(begin, incremental, store)
        if begin or end:
            sdk.search_filters.append(create_time_range_filter(EventTimestamp, begin, end))
    print([str(f) for f in sdk.search_filters])
    extractor.extract(*sdk.search_filters)
    if handlers.TOTAL_EVENTS == 0 and not errors.ERRORED:
        logger.print_info(u"No results found.")


@security_data.command()
@sdk_options
def clear_checkpoint(sdk):
    FileEventCursorStore(sdk.profile.name).replace_stored_cursor_timestamp(None)
