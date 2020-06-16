import click

from code42cli.sdk_client import sdk_options
from code42cli.cmds.search_shared import logger_factory, args
from code42cli.cmds.securitydata_mod.extraction import extract
from code42cli.date_helper import parse_min_timestamp, parse_max_timestamp
from code42cli.cmds.search_shared.enums import ExposureType


class DictObject(object):
    def __init__(self, _dict):
        self.__dict__ = _dict


@click.group()
@sdk_options
def security_data(sdk):
    pass


@security_data.command("print")
@sdk_options
@click.option("-f", "--format", type=click.Choice(["JSON", "RAW-JSON", "CEF"]))
@click.option(
    "-b", "--begin", callback=parse_min_timestamp,
)
@click.option("-e", "--end", callback=parse_max_timestamp)
@click.option("-i", "--incremental", is_flag=True)
@click.option("--advanced-query")
@click.option("-t", "--type", type=click.Choice(list(ExposureType())))
@click.option("--c42-username")
@click.option("--actor")
@click.option("--md5")
@click.option("--sha256")
@click.option("--source")
@click.option("--file-name")
@click.option("--file-path")
@click.option("--process-owner")
@click.option("--tab-url")
@click.option("--include-non-exposure", is_flag=True)
@click.pass_context
def _print(ctx, sdk, **kwargs):
    """Print file events to stdout."""
    args = DictObject(dict())
    args.format = None
    args.begin = None
    args.end = None
    args.incremental = None
    args.advanced_query = None
    args.type = None
    args.c42_username = None
    args.actor = None
    args.md5 = None
    args.sha256 = None
    args.source = None
    args.file_name = None
    args.file_path = None
    args.process_owner = None
    args.tab_url = None
    args.include_non_exposure = None
    # logger = logger_factory.get_logger_for_stdout(format)
    # extract(sdk, sdk.profile, logger, args)
    print(kwargs)
