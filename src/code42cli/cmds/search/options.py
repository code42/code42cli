import json
from datetime import datetime
from datetime import timezone

import click
from py42.sdk.queries.query_filter import FilterGroup

from code42cli.click_ext.options import incompatible_with
from code42cli.click_ext.types import FileOrString
from code42cli.logger.enums import ServerProtocol
from code42cli.output_formats import SendToFileEventsOutputFormat


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


AdvancedQueryAndSavedSearchIncompatible = incompatible_with(
    ["advanced_query", "saved_search"]
)


class BeginOption(AdvancedQueryAndSavedSearchIncompatible):
    """click.Option subclass that enforces correct --begin option usage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        # if ctx.obj is None it means we're in autocomplete mode and don't want to validate
        if (
            ctx.obj is not None
            and "saved_search" not in opts
            and "advanced_query" not in opts
        ):
            profile = opts.get("profile") or ctx.obj.profile.name
            cursor = ctx.obj.cursor_getter(profile)
            checkpoint_arg_present = "use_checkpoint" in opts
            checkpoint_value = (
                cursor.get(opts.get("use_checkpoint", ""))
                if checkpoint_arg_present
                else None
            )
            begin_present = "begin" in opts
            if (
                checkpoint_arg_present
                and checkpoint_value is not None
                and begin_present
            ):
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
            if (
                checkpoint_arg_present
                and checkpoint_value is None
                and not begin_present
            ):
                raise click.UsageError(
                    message="--begin date is required for --use-checkpoint when no checkpoint "
                    "exists yet.",
                )
            if not checkpoint_arg_present and not begin_present:
                raise click.UsageError(message="--begin date is required.")
        return super().handle_parse_result(ctx, opts, args)


def _parse_query_from_json(ctx, param, arg):
    if arg is None:
        return
    try:
        query = json.loads(arg)
        filter_groups = [FilterGroup.from_dict(group) for group in query["groups"]]
        return filter_groups
    except json.JSONDecodeError as json_error:
        raise click.BadParameter("Unable to parse JSON: {}".format(json_error))
    except KeyError as key_error:
        raise click.BadParameter(
            "Unable to build query from input JSON: {}".format(key_error)
        )


def advanced_query_option(term, **kwargs):
    defaults = dict(
        help=f"A raw JSON {term} query. "
        "Useful for when the provided query parameters do not satisfy your requirements. "
        "Argument can be passed as a string, read from stdin by passing '-', or from a filename if "
        "prefixed with '@', e.g. '--advanced-query @query.json'. "
        "WARNING: Using advanced queries is incompatible with other query-building arguments.",
        metavar="QUERY_JSON",
        type=FileOrString(),
        callback=_parse_query_from_json,
    )
    defaults.update(kwargs)
    return click.option("--advanced-query", **defaults)


def server_options(f):
    hostname_arg = click.argument("hostname")
    protocol_option = click.option(
        "-p",
        "--protocol",
        type=click.Choice(ServerProtocol(), case_sensitive=False),
        default=ServerProtocol.UDP,
        help="Protocol used to send logs to server. "
        "Use TCP-TLS for additional security. Defaults to UDP.",
    )
    certs_option = click.option(
        "--certs",
        type=str,
        help="A CA certificates-chain file for the TCP-TLS protocol.",
    )
    ignore_cert_validation = click.option(
        "--ignore-cert-validation",
        help="Set to skip CA certificate validation. "
        "Incompatible with the 'certs' option.",
        is_flag=True,
        default=None,
        cls=incompatible_with(["certs"]),
    )
    f = hostname_arg(f)
    f = protocol_option(f)
    f = certs_option(f)
    f = ignore_cert_validation(f)
    return f


send_to_format_options = click.option(
    "-f",
    "--format",
    type=click.Choice(SendToFileEventsOutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to RAW-JSON format.",
    default=SendToFileEventsOutputFormat.RAW,
)
