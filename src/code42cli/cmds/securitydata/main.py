from code42cli.args import ArgConfig
from code42cli.cmds.securitydata import enums, logger_factory
from code42cli.cmds.securitydata.extraction import extract
from code42cli.cmds.shared.cursor_store import FileEventCursorStore
from code42cli.commands import Command


def load_subcommands():
    """Sets up the `security-data` subcommand with all of its subcommands."""
    usage_prefix = u"code42 security-data"

    print_func = Command(
        u"print",
        u"Print file events to stdout",
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
    """Removes the stored checkpoint that keeps track of the last event you got.
        To use, run `code42 security-data clear-checkpoint`.
        This affects `incremental` mode by causing it to behave like it has never been run before.
    """
    FileEventCursorStore(profile.name).replace_stored_insertion_timestamp(None)


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
        enums.SearchArguments.ADVANCED_QUERY: ArgConfig(
            u"--{}".format(enums.SearchArguments.ADVANCED_QUERY.replace(u"_", u"-")),
            help=u"A raw JSON file event query. "
            u"Useful for when the provided query parameters do not satisfy your requirements."
            u"WARNING: Using advanced queries ignores all other query parameters.",
        ),
        enums.SearchArguments.BEGIN_DATE: ArgConfig(
            u"-b",
            u"--{}".format(enums.SearchArguments.BEGIN_DATE),
            help=u"The beginning of the date range in which to look for events, "
            u"can be a date/time in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format "
            u"or a short value representing days (30d), hours (24h) or minutes (15m) from current "
            u"time.",
        ),
        enums.SearchArguments.END_DATE: ArgConfig(
            u"-e",
            u"--{}".format(enums.SearchArguments.END_DATE),
            help=u"The end of the date range in which to look for events, "
            u"can be a date/time in YYYY-MM-DD (UTC) or YYYY-MM-DD HH:MM:SS (UTC+24-hr time) format "
            u"or a short value representing days (30d), hours (24h) or minutes (15m) from current "
            u"time.",
        ),
        enums.SearchArguments.EXPOSURE_TYPES: ArgConfig(
            u"-t",
            u"--{}".format(enums.SearchArguments.EXPOSURE_TYPES),
            nargs=u"+",
            help=u"Limits events to those with given exposure types. "
            u"Available choices={0}".format(list(enums.ExposureType())),
        ),
        enums.SearchArguments.C42_USERNAME: ArgConfig(
            u"--{}".format(enums.SearchArguments.C42_USERNAME.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to endpoint events for these users.",
        ),
        enums.SearchArguments.ACTOR: ArgConfig(
            u"--{}".format(enums.SearchArguments.ACTOR),
            nargs=u"+",
            help=u"Limits events to only those enacted by the cloud service user of the person who caused the event.",
        ),
        enums.SearchArguments.MD5: ArgConfig(
            u"--{}".format(enums.SearchArguments.MD5),
            nargs=u"+",
            help=u"Limits events to file events where the file has one of these MD5 hashes.",
        ),
        enums.SearchArguments.SHA256: ArgConfig(
            u"--{}".format(enums.SearchArguments.SHA256),
            nargs=u"+",
            action=u"store",
            help=u"Limits events to file events where the file has one of these SHA256 hashes.",
        ),
        enums.SearchArguments.SOURCE: ArgConfig(
            u"--{}".format(enums.SearchArguments.SOURCE),
            nargs=u"+",
            help=u"Limits events to only those from one of these sources. Example=Gmail.",
        ),
        enums.SearchArguments.FILE_NAME: ArgConfig(
            u"--{}".format(enums.SearchArguments.FILE_NAME.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to file events where the file has one of these names.",
        ),
        enums.SearchArguments.FILE_PATH: ArgConfig(
            u"--{}".format(enums.SearchArguments.FILE_PATH.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to file events where the file is located at one of these paths.",
        ),
        enums.SearchArguments.PROCESS_OWNER: ArgConfig(
            u"--{}".format(enums.SearchArguments.PROCESS_OWNER.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to exposure events where one of these users "
            u"owns the process behind the exposure.",
        ),
        enums.SearchArguments.TAB_URL: ArgConfig(
            u"--{}".format(enums.SearchArguments.TAB_URL.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to be exposure events with one of these destination tab URLs.",
        ),
        enums.SearchArguments.INCLUDE_NON_EXPOSURE_EVENTS: ArgConfig(
            u"--include-non-exposure",
            action=u"store_true",
            help=u"Get all events including non-exposure events.",
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
            help=u"Only get events that were not previously retrieved.",
        ),
    }

    arg_collection.extend(search_args)
