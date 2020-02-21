from c42sec._internal.logger_factory import get_logger_for_file
from c42sec._internal.arguments import add_all_arguments_to_parser
from c42sec._internal.extraction import extract


def init(subcommand_parser):
    """Sets up the `write-to` subcommand for writing logs to a file.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser
    """
    parser = subcommand_parser.add_parser("write-to")
    parser.set_defaults(func=write_to)
    _add_filename_subcommand(parser)
    add_all_arguments_to_parser(parser)


def write_to(args):
    """Activates 'write-to' command. It gets security events and writes them to the given file."""
    logger = get_logger_for_file(args.filename, args.format)
    extract(logger, args)


def _add_filename_subcommand(parser):
    parser.add_argument(
        action="store", dest="filename", help="The name of the local file to send output to."
    )
