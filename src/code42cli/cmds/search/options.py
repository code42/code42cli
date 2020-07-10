import json
from datetime import datetime, timezone

import click

from code42cli.cmds.search.enums import ServerProtocol
from code42cli.date_helper import parse_min_timestamp, parse_max_timestamp
from code42cli.logger import get_main_cli_logger
from code42cli.options import incompatible_with

logger = get_main_cli_logger()


def is_in_filter(filter_cls):
    def callback(ctx, param, arg):
        if arg:
            ctx.obj.search_filters.append(filter_cls.is_in(arg))
        return arg

    return callback


def not_in_filter(filter_cls):
    def callback(ctx, param, arg):
        if arg:
            ctx.obj.search_filters.append(filter_cls.not_in(arg))
        return arg

    return callback


def exists_filter(filter_cls):
    def callback(ctx, param, arg):
        if not arg:
            ctx.obj.search_filters.append(filter_cls.exists())
            return arg

    return callback


def contains_filter(filter_cls):
    def callback(ctx, param, arg):
        if arg:
            for item in arg:
                ctx.obj.search_filters.append(filter_cls.contains(item))
        return arg

    return callback


def not_contains_filter(filter_cls):
    def callback(ctx, param, arg):
        if arg:
            for item in arg:
                ctx.obj.search_filters.append(filter_cls.not_contains(item))
        return arg

    return callback


def validate_advanced_query_is_json(ctx, param, arg):
    if arg is None:
        return
    try:
        json.loads(arg)
        return arg
    except json.JSONDecodeError:
        raise click.ClickException("Failed to parse advanced query, must be a valid json string.")


AdvancedQueryAndSavedSearchIncompatible = incompatible_with(["advanced_query", "saved_search"])


class BeginOption(AdvancedQueryAndSavedSearchIncompatible):
    """click.Option subclass that enforces correct --begin option usage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        # if ctx.obj is None it means we're in autocomplete mode and don't want to validate
        if ctx.obj is not None and "saved_search" not in opts and "advanced_query" not in opts:
            profile = opts.get("profile") or ctx.obj.profile.name
            cursor = ctx.obj.cursor_getter(profile)
            checkpoint_arg_present = "use_checkpoint" in opts
            checkpoint_value = (
                cursor.get(opts.get("use_checkpoint", "")) if checkpoint_arg_present else None
            )
            begin_present = "begin" in opts
            if checkpoint_arg_present and checkpoint_value is not None and begin_present:
                opts.pop("begin")
                checkpoint_value_str = datetime.fromtimestamp(
                    checkpoint_value, timezone.utc
                ).isoformat()
                click.echo(
                    "Ignoring --begin value as --use-checkpoint was passed and checkpoint of {} exists.\n".format(
                        checkpoint_value_str
                    ),
                    err=True,
                )
            if checkpoint_arg_present and checkpoint_value is None and not begin_present:
                raise click.UsageError(
                    message="--begin date is required for --use-checkpoint when no checkpoint "
                    "exists yet.",
                )
            if not checkpoint_arg_present and not begin_present:
                raise click.UsageError(message="--begin date is required.")
        return super().handle_parse_result(ctx, opts, args)


def create_search_options(search_term):
    begin_option = click.option(
        "-b",
        "--begin",
        callback=lambda ctx, param, arg: parse_min_timestamp(arg),
        cls=BeginOption,
        help="The beginning of the date range in which to look for {}, can be a date/time in "
        "yyyy-MM-dd (UTC) or yyyy-MM-dd HH:MM:SS (UTC+24-hr time) format where the 'time' "
        "portion of the string can be partial (e.g. '2020-01-01 12' or '2020-01-01 01:15') "
        "or a short value representing days (30d), hours (24h) or minutes (15m) from current "
        "time.".format(search_term),
    )
    end_option = click.option(
        "-e",
        "--end",
        callback=lambda ctx, param, arg: parse_max_timestamp(arg),
        cls=AdvancedQueryAndSavedSearchIncompatible,
        help="The end of the date range in which to look for {}, argument format options are "
        "the same as --begin.".format(search_term),
    )
    advanced_query_option = click.option(
        "--advanced-query",
        help="\b\nA raw JSON {} query. "
        "Useful for when the provided query parameters do not satisfy your requirements."
        "\nWARNING: Using advanced queries is incompatible with other query-building args.".format(
            search_term
        ),
        callback=validate_advanced_query_is_json,
    )
    checkpoint_option = click.option(
        "-c",
        "--use-checkpoint",
        cls=AdvancedQueryAndSavedSearchIncompatible,
        help="Only get {0} that were not previously retrieved.".format(search_term),
    )

    def search_options(f):
        f = begin_option(f)
        f = end_option(f)
        f = checkpoint_option(f)
        f = advanced_query_option(f)
        return f

    return search_options
