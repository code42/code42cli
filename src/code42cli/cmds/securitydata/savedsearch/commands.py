from py42.util import format_json

from code42cli.commands import Command, SubcommandLoader
from code42cli.util import format_to_table, find_format_width
from code42cli.logger import get_main_cli_logger


class SavedSearchSubCommandLoader(SubcommandLoader):
    LIST = u"list"
    PRINT = u"print"
    WRITE_TO = u"write-to"
    SEND_TO = u"send-to"
    CLEAR_CHECKPOINT = u"clear-checkpoint"
    SHOW = u"show"
    EXECUTE = u"execute"
    
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
            "Get detials of saved searches.",
            u"{} {} {}".format(usage_prefix, self.SHOW, u"<search-id>"),
            handler=show_detail,
            arg_customizer=_load_search_id_args,
        )
        
        execute_command = Command(
            self.EXECUTE,
            "Execute a saved search.",
            u"{} {} {}".format(usage_prefix, self.EXECUTE, u"<search-id>"),
            handler=execute,
            arg_customizer=_load_search_id_args,
        )
        return [list_command, show_command, execute_command]


def show(sdk, profile):
    response = sdk.securitydata.savedsearches.get()
    header = {u"name": u"Name", u"id": u"Id"}
    return format_to_table(*find_format_width(response[u"searches"], header))


def show_detail(sdk, profile, search_id):
    response = sdk.securitydata.savedsearches.get_by_id(search_id)
    logger = get_main_cli_logger()
    logger.print_info(format_json(response.text))


def execute(sdk, profile, search_id):
    response = sdk.securitydata.savedsearches.execute(search_id)
    logger = get_main_cli_logger()
    logger.print_info(format_json(response["fileEvents"]))


def _load_search_id_args(argument_collection):
    search_id = argument_collection.arg_configs[u"search_id"]
    search_id.set_help(u"The id of the saved search.")
