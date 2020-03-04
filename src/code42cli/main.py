from argparse import ArgumentParser

from code42cli.compat import str
from code42cli.profile import profile
import code42cli.securitydata.main as securitydata


def main():
    code42_arg_parser = ArgumentParser()
    subcommand_parser = code42_arg_parser.add_subparsers()
    profile.init(subcommand_parser)
    securitydata.init_subcommand(subcommand_parser)
    _run(code42_arg_parser)


def _run(parser):
    try:
        args = parser.parse_args()
        args.func(args)
    except AttributeError as ex:
        if str(ex) == "'Namespace' object has no attribute 'func'":
            parser.print_help()
            return
        raise ex
