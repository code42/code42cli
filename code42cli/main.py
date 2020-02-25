from argparse import ArgumentParser

from code42cli.profile import profile
import code42cli.securitydata.main as securitydata


def main():
    code42_arg_parser = ArgumentParser()
    subcommand_parser = code42_arg_parser.add_subparsers()
    profile.init(subcommand_parser)
    securitydata.init_subcommand(subcommand_parser)
    args = code42_arg_parser.parse_args()
    args.func(args)
