from argparse import ArgumentParser

from code42cli.subcommands import profile
import code42cli.subcommands.securitydata.main as securitydata


def main():
    code42_arg_parser = ArgumentParser()
    subcommand_parser = code42_arg_parser.add_subparsers()
    _init_subcommands(subcommand_parser)
    _call_subcommand(code42_arg_parser)


def _init_subcommands(subcommand_parser):
    profile.init(subcommand_parser)
    securitydata.init_subcommand(subcommand_parser)


def _call_subcommand(arg_parser):
    """Call provided subcommand with args."""
    args = arg_parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
