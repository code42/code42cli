from code42cli.arguments import add_profile_name_arg
from code42cli.profile.profile import get_profile
from code42cli.securitydata.cursor_store import FileEventCursorStore


def init(subcommand_parser):
    """Sets up the `clear-checkpoint` subcommand for cleared the stored checkpoint for `incremental` mode.
        Args:
            subcommand_parser: The subparsers group created by the parent parser.
    """
    parser = subcommand_parser.add_parser(
        u"clear-checkpoint",
        description=u"Remove the saved checkpoint from 'incremental' (-i) mode.",
        usage=u"code42 securitydata clear-checkpoint <optional-args>",
    )
    add_profile_name_arg(parser)
    parser.set_defaults(func=clear_checkpoint)


def clear_checkpoint(args):
    """Removes the stored checkpoint that keeps track of the last event you got.
        To use, run `code42 clear-checkpoint`.
        This affects `incremental` mode by causing it to behave like it has never been run before.
    """
    profile_name = args.profile_name or get_profile().name
    FileEventCursorStore(profile_name).replace_stored_insertion_timestamp(None)
