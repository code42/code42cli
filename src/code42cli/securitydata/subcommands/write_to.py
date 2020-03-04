from code42cli.securitydata.logger_factory import get_logger_for_file
from code42cli.securitydata.arguments import main as main_args
from code42cli.securitydata.arguments import search as search_args
from code42cli.securitydata.extraction import extract


def init(subcommand_parser):
    """Sets up the `write-to` subcommand for writing logs to a file.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser.
    """
    parser = subcommand_parser.add_parser(u"write-to")
    parser.set_defaults(func=write_to)
    _add_filename_subcommand(parser)
    search_args.add_arguments_to_parser(parser)
    main_args.add_arguments_to_parser(parser)


def write_to(args):
    """Activates 'write-to' command. It gets security events and writes them to the given file."""
    logger = get_logger_for_file(args.output_file, args.format)
    extract(logger, args)


def _add_filename_subcommand(parser):
    parser.add_argument(
        action=u"store", dest=u"output_file", help=u"The name of the local file to send output to."
    )
