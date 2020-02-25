from code42cli.securitydata.logger_factory import get_logger_for_stdout
from code42cli.securitydata.arguments import search as search_args
from code42cli.securitydata.arguments import main as main_args
from code42cli.securitydata.extraction import extract


def init(subcommand_parser):
    """Sets up the `print` subcommand.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser.
    """
    parser = subcommand_parser.add_parser("print")
    parser.set_defaults(func=print_out)
    search_args.add_arguments_to_parser(parser)
    main_args.add_arguments_to_parser(parser)


def print_out(args):
    """Activates 'print' command. It gets security events and prints them to stdout."""
    logger = get_logger_for_stdout(args.format)
    extract(logger, args)
