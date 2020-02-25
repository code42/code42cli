from argparse import ArgumentParser

from code42cli.profile import profile
import code42cli.securitydata.main as securitydata


def main():
    code42_arg_parser = ArgumentParser()
    _add_debug_args(code42_arg_parser)
    subcommand_parser = code42_arg_parser.add_subparsers()
    profile.init(subcommand_parser)
    securitydata.init_subcommand(subcommand_parser)
    _call_subcommand(code42_arg_parser)


def _call_subcommand(parser):
    try:
        args = parser.parse_args()
        args.func(args)
    except AttributeError as ex:
        if str(ex) == "'Namespace' object has no attribute 'func'":
            parser.print_help()
            return
        raise ex


def _add_debug_args(parser):
    parser.add_argument(
        "-d", "--debug", dest="is_debug_mode", action="store_true", help="Turn on Debug logging."
    )
