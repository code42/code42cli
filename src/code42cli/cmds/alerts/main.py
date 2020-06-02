from code42cli.args import ArgConfig
from code42cli.commands import Command, SubcommandLoader
from code42cli.cmds.alerts.extraction import extract
from code42cli.cmds.search_shared import args, logger_factory
from code42cli.cmds.search_shared.enums import (
    AlertFilterArguments,
    AlertState,
    AlertSeverity,
    ServerProtocol,
    RuleType,
)
from code42cli.cmds.search_shared.cursor_store import AlertCursorStore


class MainAlertsSubcommandLoader(SubcommandLoader):
    PRINT = u"print"
    WRITE_TO = u"write-to"
    SEND_TO = u"send-to"
    CLEAR_CHECKPOINT = u"clear-checkpoint"

    def load_commands(self):
        """Sets up the `alerts` subcommand with all of its subcommands."""
        usage_prefix = u"code42 alerts"

        print_func = Command(
            self.PRINT,
            u"Print alerts to stdout",
            u"{} {}".format(usage_prefix, u"print <optional-args>"),
            handler=print_out,
            arg_customizer=_load_search_args,
            use_single_arg_obj=True,
        )

        write = Command(
            self.WRITE_TO,
            u"Write alerts to the file with the given name.",
            u"{} {}".format(usage_prefix, u"write-to <filename> <optional-args>"),
            handler=write_to,
            arg_customizer=_load_write_to_args,
            use_single_arg_obj=True,
        )

        send = Command(
            self.SEND_TO,
            u"Send alerts to the given server address.",
            u"{} {}".format(usage_prefix, u"send-to <server-address> <optional-args>"),
            handler=send_to,
            arg_customizer=_load_send_to_args,
            use_single_arg_obj=True,
        )

        clear = Command(
            self.CLEAR_CHECKPOINT,
            u"Remove the saved alert checkpoint from 'incremental' (-i) mode.",
            u"{} {}".format(usage_prefix, u"clear-checkpoint <optional-args>"),
            handler=clear_checkpoint,
        )

        return [print_func, write, send, clear]


def clear_checkpoint(sdk, profile):
    """Removes the stored checkpoint that keeps track of the last alert retrieved for the given profile..
        To use, run `code42 alerts clear-checkpoint`.
        This affects `incremental` mode by causing it to behave like it has never been run before.
    """
    AlertCursorStore(profile.name).replace_stored_cursor_timestamp(None)


def print_out(sdk, profile, args):
    """Activates 'print' command. It gets alerts and prints them to stdout."""
    logger = logger_factory.get_logger_for_stdout(args.format)
    extract(sdk, profile, logger, args)


def write_to(sdk, profile, args):
    """Activates 'write-to' command. It gets alerts and writes them to the given file."""
    logger = logger_factory.get_logger_for_file(args.output_file, args.format)
    extract(sdk, profile, logger, args)


def send_to(sdk, profile, args):
    """Activates 'send-to' command. It getsalerts and logs them to the given server."""
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
            choices=ServerProtocol(),
            default=ServerProtocol.UDP,
            help=u"Protocol used to send logs to server.",
        ),
    }

    arg_collection.extend(send_to_args)
    _load_search_args(arg_collection)


def _load_search_args(arg_collection):
    filter_args = {
        AlertFilterArguments.SEVERITY: ArgConfig(
            u"--{}".format(AlertFilterArguments.SEVERITY),
            nargs=u"+",
            help=u"Filter alerts by severity. Defaults to returning all severities. Available choices={0}.".format(
                list(AlertSeverity())
            ),
        ),
        AlertFilterArguments.STATE: ArgConfig(
            u"--{}".format(AlertFilterArguments.STATE),
            help=u"Filter alerts by state. Defaults to returning all states. Available choices={0}.".format(
                list(AlertState())
            ),
        ),
        AlertFilterArguments.ACTOR: ArgConfig(
            u"--{}".format(AlertFilterArguments.ACTOR.replace("_", "-")),
            metavar=u"ACTOR",
            help=u"Filter alerts by including the given actor(s) who triggered the alert. Args must match actor username exactly.",
            nargs=u"+",
        ),
        AlertFilterArguments.ACTOR_CONTAINS: ArgConfig(
            u"--{}".format(AlertFilterArguments.ACTOR_CONTAINS.replace("_", "-")),
            metavar=u"ACTOR",
            help=u"Filter alerts by including actor(s) whose username contains the given string.",
            nargs=u"+",
        ),
        AlertFilterArguments.EXCLUDE_ACTOR: ArgConfig(
            u"--{}".format(AlertFilterArguments.EXCLUDE_ACTOR.replace("_", "-")),
            metavar=u"ACTOR",
            help=u"Filter alerts by excluding the given actor(s) who triggered the alert. Args must match actor username exactly.",
            nargs=u"+",
        ),
        AlertFilterArguments.EXCLUDE_ACTOR_CONTAINS: ArgConfig(
            u"--{}".format(AlertFilterArguments.EXCLUDE_ACTOR_CONTAINS.replace("_", "-")),
            metavar=u"ACTOR",
            help=u"Filter alerts by excluding actor(s) whose username contains the given string.",
            nargs=u"+",
        ),
        AlertFilterArguments.RULE_NAME: ArgConfig(
            u"--{}".format(AlertFilterArguments.RULE_NAME.replace("_", "-")),
            metavar=u"RULE_NAME",
            help=u"Filter alerts by including the given rule name(s).",
            nargs=u"+",
        ),
        AlertFilterArguments.EXCLUDE_RULE_NAME: ArgConfig(
            u"--{}".format(AlertFilterArguments.EXCLUDE_RULE_NAME.replace("_", "-")),
            metavar=u"RULE_NAME",
            help=u"Filter alerts by excluding the given rule name(s).",
            nargs=u"+",
        ),
        AlertFilterArguments.RULE_ID: ArgConfig(
            u"--{}".format(AlertFilterArguments.RULE_ID.replace("_", "-")),
            metavar=u"RULE_ID",
            help=u"Filter alerts by including the given rule id(s).",
            nargs=u"+",
        ),
        AlertFilterArguments.EXCLUDE_RULE_ID: ArgConfig(
            u"--{}".format(AlertFilterArguments.EXCLUDE_RULE_ID.replace("_", "-")),
            metavar=u"RULE_ID",
            help=u"Filter alerts by excluding the given rule id(s).",
            nargs=u"+",
        ),
        AlertFilterArguments.RULE_TYPE: ArgConfig(
            u"--{}".format(AlertFilterArguments.RULE_TYPE.replace("_", "-")),
            metavar=u"RULE_TYPE",
            help=u"Filter alerts by including the given rule type(s). Available choices={0}.".format(
                list(RuleType())
            ),
            nargs=u"+",
        ),
        AlertFilterArguments.EXCLUDE_RULE_TYPE: ArgConfig(
            u"--{}".format(AlertFilterArguments.EXCLUDE_RULE_TYPE.replace("_", "-")),
            metavar=u"RULE_TYPE",
            help=u"Filter alerts by excluding the given rule type(s). Available choices={0}.".format(
                list(RuleType())
            ),
            nargs=u"+",
        ),
        AlertFilterArguments.DESCRIPTION: ArgConfig(
            u"--{}".format(AlertFilterArguments.DESCRIPTION),
            help=u"Filter alerts by description. Does fuzzy search by default.",
        ),
    }
    search_args = args.create_search_args(search_for=u"alerts", filter_args=filter_args)
    arg_collection.extend(search_args)
