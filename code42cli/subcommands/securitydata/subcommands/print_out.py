from code42cli.subcommands.securitydata.logger_factory import get_logger_for_stdout
from code42cli.subcommands.securitydata.arguments import add_all_arguments_to_parser
from code42cli.subcommands.securitydata.extraction import extract


def init(subcommand_parser):
    """Sets up the `print` subcommand.
            Use `-h` after any subcommand for usage.
        Args:
            subcommand_parser: The subparsers group created by the parent parser.
    """
    parser = subcommand_parser.add_parser("print")
    parser.set_defaults(func=print_out)
    add_all_arguments_to_parser(parser)


def print_out(args):
    """Activates 'print' command. It gets security events and prints them to STDOUT."""
    logger = get_logger_for_stdout(args.format)
    extract(logger, args)
