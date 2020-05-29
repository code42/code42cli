from code42cli.args import ArgConfig
from code42cli.cmds.search_shared import logger_factory, args
from code42cli.cmds.search_shared.enums import (
    FileEventFilterArguments,
    ServerProtocol,
    ExposureType,
)
from code42cli.cmds.securitydata.extraction import extract
from code42cli.cmds.search_shared.cursor_store import FileEventCursorStore
from code42cli.commands import Command, SubcommandLoader


class SecurityDataSubcommandLoader(SubcommandLoader):
    PRINT = u"print"
    WRITE_TO = u"write-to"
    SEND_TO = u"send-to"
    CLEAR_CHECKPOINT = u"clear-checkpoint"

    def load_commands(self):
        """Sets up the `security-data` subcommand with all of its subcommands."""
        usage_prefix = u"code42 security-data"

        print_func = Command(
            self.PRINT,
            u"Print file events to stdout.",
            u"{} {}".format(usage_prefix, u"print <optional-args>"),
            handler=print_out,
            arg_customizer=_load_search_args,
            use_single_arg_obj=True,
        )

        write = Command(
            self.WRITE_TO,
            u"Write file events to the file with the given name.",
            u"{} {}".format(usage_prefix, u"write-to <filename> <optional-args>"),
            handler=write_to,
            arg_customizer=_load_write_to_args,
            use_single_arg_obj=True,
        )

        send = Command(
            self.SEND_TO,
            u"Send file events to the given server address.",
            u"{} {}".format(usage_prefix, u"send-to <server-address> <optional-args>"),
            handler=send_to,
            arg_customizer=_load_send_to_args,
            use_single_arg_obj=True,
        )

        clear = Command(
            self.CLEAR_CHECKPOINT,
            u"Remove the saved file event checkpoint from 'incremental' (-i) mode.",
            u"{} {}".format(usage_prefix, u"clear-checkpoint <optional-args>"),
            handler=clear_checkpoint,
        )

        return [print_func, write, send, clear]


def clear_checkpoint(sdk, profile):
    """Removes the stored checkpoint that keeps track of the last file event retrieved for the given profile.
        To use, run `code42 security-data clear-checkpoint`.
        This affects `incremental` mode by causing it to behave like it has never been run before.
    """
    FileEventCursorStore(profile.name).replace_stored_cursor_timestamp(None)


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
            choices=ServerProtocol(),
            default=ServerProtocol.UDP,
            help=u"Protocol used to send logs to server.",
        ),
    }

    arg_collection.extend(send_to_args)
    _load_search_args(arg_collection)


def _load_search_args(arg_collection):
    filter_args = {
        FileEventFilterArguments.EXPOSURE_TYPES: ArgConfig(
            u"-t",
            u"--{}".format(FileEventFilterArguments.EXPOSURE_TYPES),
            nargs=u"+",
            help=u"Limits events to those with given exposure types. "
            u"Available choices={0}".format(list(ExposureType())),
        ),
        FileEventFilterArguments.C42_USERNAME: ArgConfig(
            u"--{}".format(FileEventFilterArguments.C42_USERNAME.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to endpoint events for these users.",
        ),
        FileEventFilterArguments.ACTOR: ArgConfig(
            u"--{}".format(FileEventFilterArguments.ACTOR),
            nargs=u"+",
            help=u"Limits events to only those enacted by the cloud service user of the person who caused the event.",
        ),
        FileEventFilterArguments.MD5: ArgConfig(
            u"--{}".format(FileEventFilterArguments.MD5),
            nargs=u"+",
            help=u"Limits events to file events where the file has one of these MD5 hashes.",
        ),
        FileEventFilterArguments.SHA256: ArgConfig(
            u"--{}".format(FileEventFilterArguments.SHA256),
            nargs=u"+",
            action=u"store",
            help=u"Limits events to file events where the file has one of these SHA256 hashes.",
        ),
        FileEventFilterArguments.SOURCE: ArgConfig(
            u"--{}".format(FileEventFilterArguments.SOURCE),
            nargs=u"+",
            help=u"Limits events to only those from one of these sources. Example=Gmail.",
        ),
        FileEventFilterArguments.FILE_NAME: ArgConfig(
            u"--{}".format(FileEventFilterArguments.FILE_NAME.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to file events where the file has one of these names.",
        ),
        FileEventFilterArguments.FILE_PATH: ArgConfig(
            u"--{}".format(FileEventFilterArguments.FILE_PATH.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to file events where the file is located at one of these paths.",
        ),
        FileEventFilterArguments.PROCESS_OWNER: ArgConfig(
            u"--{}".format(FileEventFilterArguments.PROCESS_OWNER.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to exposure events where one of these users "
            u"owns the process behind the exposure.",
        ),
        FileEventFilterArguments.TAB_URL: ArgConfig(
            u"--{}".format(FileEventFilterArguments.TAB_URL.replace(u"_", u"-")),
            nargs=u"+",
            help=u"Limits events to be exposure events with one of these destination tab URLs.",
        ),
        FileEventFilterArguments.INCLUDE_NON_EXPOSURE_EVENTS: ArgConfig(
            u"--include-non-exposure",
            action=u"store_true",
            help=u"Get all events including non-exposure events.",
        ),
    }
    search_args = args.create_search_args(search_for=u"file events", filter_args=filter_args)
    arg_collection.extend(search_args)
