from c42sec._internal.logger_factory import get_logger_for_stdout
from c42sec._internal.args import add_args
from c42sec._internal.extraction import extract_to_destination


def init(subcommand_parser):
    parser = subcommand_parser.add_parser("print")
    parser.set_defaults(func=print_out)
    add_args(parser)


def print_out(args):
    logger = get_logger_for_stdout(args.format)
    extract_to_destination(logger, args)
