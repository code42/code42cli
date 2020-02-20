from c42sec._internal.logger_factory import get_logger_for_stdout
from c42sec._internal.arguments import add_all_arguments_to_parser
from c42sec._internal.extraction import extract


def init(subcommand_parser):
    parser = subcommand_parser.add_parser("print")
    parser.set_defaults(func=print_out)
    add_all_arguments_to_parser(parser)


def print_out(args):
    logger = get_logger_for_stdout(args.format)
    extract(logger, args)
