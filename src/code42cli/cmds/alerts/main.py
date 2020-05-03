from code42cli.args import ArgConfig
from code42cli.commands import Command
from code42cli.cmds.alerts.extraction import extract
from code42cli.cmds.shared import enums, logger_factory
from code42cli.cmds.shared.cursor_store import AlertCursorStore


def load_subcommands():
    """Sets up the `alerts` subcommand with all of its subcommands."""
    usage_prefix = u"code42 alerts"

    print_func = Command(
        u"print",
        u"Print alerts to stdout",
        u"{} {}".format(usage_prefix, u"print <optional-args>"),
        handler=print_out,
        arg_customizer=_load_search_args,
        use_single_arg_obj=True,
    )

    write = Command(
        u"write-to",
        u"Write file events to the file with the given name.",
        u"{} {}".format(usage_prefix, u"write-to <filename> <optional-args>"),
        handler=write_to,
        arg_customizer=_load_write_to_args,
        use_single_arg_obj=True,
    )

    send = Command(
        u"send-to",
        u"Send file events to the given server address.",
        u"{} {}".format(usage_prefix, u"send-to <server-address> <optional-args>"),
        handler=send_to,
        arg_customizer=_load_send_to_args,
        use_single_arg_obj=True,
    )

    clear = Command(
        u"clear-checkpoint",
        u"Remove the saved checkpoint from 'incremental' (-i) mode.",
        u"{} {}".format(usage_prefix, u"clear-checkpoint <optional-args>"),
        handler=clear_checkpoint,
    )

    return [print_func, write, send, clear]


def clear_checkpoint(sdk, profile):
    """Removes the stored checkpoint that keeps track of the last alert you got.
        To use, run `code42 alerts clear-checkpoint`.
        This affects `incremental` mode by causing it to behave like it has never been run before.
    """
    AlertCursorStore(profile.name).replace_stored_cursor_timestamp(None)


def print_out(sdk, profile, args):
    """Activates 'print' command. It gets security events and prints them to stdout."""
    logger = logger_factory.get_logger_for_stdout(args.format)
    extract(sdk, profile, logger, args)


def write_to(sdk, profile, args):
    """Activates 'write-to' command. It gets security events and writes them to the given file."""
    logger = logger_factory.get_logger_for_file(args.output_file, args.format)
    extract(sdk, profile, logger, args)


def send_to(sdk, profile, args):
    """Activates 'send-to' command. It gets security events and logs them to the given server."""
    logger = logger_factory.get_logger_for_server(args.server, args.protocol, args.format)
    extract(sdk, profile, logger, args)


def _load_write_to_args(arg_collection):
    output_file = ArgConfig(u"output_file", help=u"The name of the local file to send output to.")
    arg_collection.append(u"output_file", output_file)
    _load_search_args(arg_collection)


def _load_send_to_args(arg_collection):
    send_to_args = {
        u"server": ArgConfig(u"server", help=u"The server address to send output to."),
        u"protocol": ArgConfig(
            u"-p",
            u"--protocol",
            choices=enums.ServerProtocol(),
            default=enums.ServerProtocol.UDP,
            help=u"Protocol used to send logs to server.",
        ),
    }

    arg_collection.extend(send_to_args)
    _load_search_args(arg_collection)


def _load_search_args(arg_collection):
    search_args = {
        enums.AlertArguments.ADVANCED_QUERY: ArgConfig(
            u"--{}".format(enums.AlertArguments.ADVANCED_QUERY.replace(u"_", u"-")),
            help=u"A raw JSON alert query. "
            u"Useful for when the provided query parameters do not satisfy your requirements."
            u"WARNING: Using advanced queries ignores all other query parameters.",
        ),
        enums.AlertArguments.BEGIN_DATE: ArgConfig(
            u"-b",
            u"--{}".format(enums.AlertArguments.BEGIN_DATE),
            help=u"The beginning of the date range in which to look for alerts, "
            u"can be a date/time in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format "
            u"or a short value representing days (30d), hours (24h) or minutes (15m) from current "
            u"time.",
        ),
        enums.AlertArguments.END_DATE: ArgConfig(
            u"-e",
            u"--{}".format(enums.AlertArguments.END_DATE),
            help=u"The end of the date range in which to look for alerts, "
            u"can be a date/time in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format "
            u"or a short value representing days (30d), hours (24h) or minutes (15m) from current "
            u"time.",
        ),
        enums.AlertArguments.SEVERITY: ArgConfig(
            u"--{}".format(enums.AlertArguments.SEVERITY),
            nargs=u"+",
            help=u"Filter alerts by severity. Defaults to returning all severities. Available choices={0}".format(
                list(enums.AlertSeverity())
            ),
        ),
        enums.AlertArguments.STATE: ArgConfig(
            u"--{}".format(enums.AlertArguments.STATE),
            help=u"Filter alerts by state. Defaults to returning all states. Available choices={0}".format(
                enums.AlertState()
            ),
        ),
        enums.AlertArguments.ACTOR_IS: ArgConfig(
            u"--{}".format(enums.AlertArguments.ACTOR_IS.replace("_", "-")),
            metavar=u"ACTOR",
            help=u"Filter alerts by including the given actor(s) who triggered the alert. Accepts multiple args. Args must match actor username exactly.",
            nargs=u"+",
        ),
        enums.AlertArguments.ACTOR_CONTAINS: ArgConfig(
            u"--{}".format(enums.AlertArguments.ACTOR_CONTAINS.replace("_", "-")),
            metavar=u"ACTOR",
            help=u"Filter alerts by including actor(s) whose username contains the given string.",
            nargs=u"+",
        ),
        enums.AlertArguments.ACTOR_NOT: ArgConfig(
            u"--{}".format(enums.AlertArguments.ACTOR_NOT.replace("_", "-")),
            metavar=u"ACTOR",
            help=u"Filter alerts by excluding the given actor(s) who triggered the alert. Accepts multiple args. Args must match actor username exactly.",
            nargs=u"+",
        ),
        enums.AlertArguments.ACTOR_NOT_CONTAINS: ArgConfig(
            u"--{}".format(enums.AlertArguments.ACTOR_NOT_CONTAINS.replace("_", "-")),
            metavar=u"ACTOR",
            help=u"Filter alerts by excluding actor(s) whose username contains the given string.",
        ),
        enums.AlertArguments.RULE_NAME_IS: ArgConfig(
            u"--{}".format(enums.AlertArguments.RULE_NAME_IS.replace("_", "-")),
            metavar=u"RULE_NAME",
            help=u"Filter alerts by including the given rule name(s). Accepts multiple args. Put a '*' at the start of an arg string to do a fuzzy search (e.g. '*search term').",
            nargs=u"+",
        ),
        enums.AlertArguments.RULE_NAME_CONTAINS: ArgConfig(
            u"--{}".format(enums.AlertArguments.RULE_NAME_CONTAINS.replace("_", "-")),
            metavar=u"RULE_NAME",
            help=u"Filter alerts by including rules that contain the given arg string in their name.",
        ),
        enums.AlertArguments.RULE_NAME_NOT: ArgConfig(
            u"--{}".format(enums.AlertArguments.RULE_NAME_NOT.replace("_", "-")),
            metavar=u"RULE_NAME",
            help=u"Filter alerts by excluding the given rule name(s). Accepts multiple args. Put a '*' at the start of an arg string to do a fuzzy search (e.g. '*search term').",
            nargs=u"+",
        ),
        enums.AlertArguments.RULE_NAME_NOT_CONTAINS: ArgConfig(
            u"--{}".format(enums.AlertArguments.RULE_NAME_NOT_CONTAINS.replace("_", "-")),
            metavar=u"RULE_NAME",
            help=u"Filter alerts by excluding rules that contain the given arg string in their name.",
        ),
        enums.AlertArguments.DESCRIPTION: ArgConfig(
            u"--{}".format(enums.AlertArguments.DESCRIPTION),
            help=u"Filter alerts by description. Does fuzzy search by default.",
        ),
        u"format": ArgConfig(
            u"-f",
            u"--format",
            choices=enums.OutputFormat(),
            default=enums.OutputFormat.JSON,
            help=u"The format used for outputting events.",
        ),
        u"incremental": ArgConfig(
            u"-i",
            u"--incremental",
            action=u"store_true",
            help=u"Only get alerts that were not previously retrieved.",
        ),
    }

    arg_collection.extend(search_args)
