from __future__ import print_function
from argparse import ArgumentParser

from c42sec._internal.compat import str
from c42sec import send_to, write_to, profile


def main():
    c42sec_arg_parser = ArgumentParser()
    subcommand_parser = c42sec_arg_parser.add_subparsers()
    _init_subcommands(subcommand_parser)
    _call_subcommand(c42sec_arg_parser)


def _init_subcommands(subcommand_parser):
    profile.init(subcommand_parser)
    send_to.init(subcommand_parser)
    write_to.init(subcommand_parser)


def _call_subcommand(arg_parser):
    """Call provided subcommand with args."""
    try:
        args = arg_parser.parse_args()
        args.func(args)
    except AttributeError as err:
        if str(err) == "'Namespace' object has no attribute 'func'":
            arg_parser.print_help()
        else:
            print(err)


if __name__ == "__main__":
    main()
