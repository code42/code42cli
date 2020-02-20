from c42sec._internal.logger_factory import get_logger_for_file
from c42sec._internal.arguments import add_args
from c42sec._internal.extraction import extract


def init(subcommand_parser):
    parser = subcommand_parser.add_parser("write-to")
    parser.set_defaults(func=write_to)
    _add_filename_subcommand(parser)
    add_args(parser)


def write_to(args):
    logger = get_logger_for_file(args.filename, args.format)
    extract(logger, args)


def _add_filename_subcommand(parser):
    parser.add_argument(
        action="store", dest="filename", help="The name of the local file to send output to."
    )
