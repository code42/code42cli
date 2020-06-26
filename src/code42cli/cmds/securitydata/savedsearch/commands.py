from code42cli.commands import Command, SubcommandLoader
from code42cli.cmds.securitydata.savedsearch.savedsearch import show, show_detail


def _load_search_id_args(argument_collection):
    search_id = argument_collection.arg_configs[u"search_id"]
    search_id.set_help(u"The id of the saved search.")


class SavedSearchSubCommandLoader(SubcommandLoader):
    LIST = u"list"
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
            "Get the details of a saved search.",
            u"{} {} {}".format(usage_prefix, self.SHOW, u"<search-id>"),
            handler=show_detail,
            arg_customizer=_load_search_id_args,
        )

        return [list_command, show_command]
