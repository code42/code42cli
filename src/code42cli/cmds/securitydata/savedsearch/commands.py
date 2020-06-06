from code42cli.args import ArgConfig
from code42cli.commands import Command, SubcommandLoader
from code42cli.cmds.search_shared.enums import ServerProtocol
from code42cli.cmds.securitydata.savedsearch.savedsearch import (
    show,
    show_detail,
    print_out,
    write_to,
    send_to,
)


def _load_search_id_args(argument_collection):
    search_id = argument_collection.arg_configs[u"search_id"]
    search_id.set_help(u"The id of the saved search.")


def _load_extraction_args(argument_collection):
    _load_search_id_args(argument_collection)
    incremental = {u"incremental": ArgConfig(
        u"-i",
        u"--incremental",
        action=u"store_true",
        help=u"Only get saved search records that were not previously retrieved.",
    )}
    argument_collection.extend(incremental)


def _load_write_to_args(argument_collection):
    _load_extraction_args(argument_collection)
    output_file = argument_collection.arg_configs[u"filename"]
    output_file.add_short_option_name(u"-f")
    output_file.set_help(u"The name of the local file to send output to.")


def _load_send_to_args(argument_collection):
    _load_extraction_args(argument_collection)
    server = argument_collection.arg_configs[u"server"]
    server.add_short_option_name(u"-s")
    server.set_help(u"The server address to send output to.")
    send_to_args = {
        u"server": server,
        u"protocol": ArgConfig(
            u"-p",
            u"--protocol",
            choices=ServerProtocol(),
            default=ServerProtocol.UDP,
            help=u"Protocol used to send logs to server.",
        ),
    }

    argument_collection.extend(send_to_args)


class SavedSearchSubCommandLoader(SubcommandLoader):
    LIST = u"list"
    PRINT = u"print"
    WRITE_TO = u"write-to"
    SEND_TO = u"send-to"
    CLEAR_CHECKPOINT = u"clear-checkpoint"
    SHOW = u"show"

    def load_commands(self):
        """Sets up security-data subcommand with all of its subcommands."""
        usage_prefix = u"code42 security-data saved-search"

        list_command = Command(
            self.LIST,
            u"List available saved searches.",
            u"{} {}".format(usage_prefix, self.LIST),
            handler=show,
        )

        show_command = Command(
            self.SHOW,
            "Get details of saved searches.",
            u"{} {} {}".format(usage_prefix, self.SHOW, u"<search-id>"),
            handler=show_detail,
            arg_customizer=_load_search_id_args,
        )

        print_command = Command(
            self.PRINT,
            u"Print saved search result to stdout.",
            u"{} {} {}".format(usage_prefix, self.SHOW, u"<search-id> <optional-args>"),
            handler=print_out,
            arg_customizer=_load_extraction_args,
        )

        send_to_command = Command(
            self.SEND_TO,
            u"Send saved search result to the given server address.",
            u"{} {} {}".format(usage_prefix, self.SEND_TO,
                               u"--search-id <search-id> --filename <filename> <optional-args>"),
            handler=send_to,
            arg_customizer=_load_send_to_args,
        )

        write_to_command = Command(
            self.WRITE_TO,
            u"Write saved search result to the file with the given name.",
            u"{} {} {}".format(usage_prefix, self.WRITE_TO,
                               u"--search-id <search-id> --server <server-address> <optional-args>"),
            handler=write_to,
            arg_customizer=_load_write_to_args,
        )

        return [list_command, show_command, print_command, send_to_command, write_to_command]
