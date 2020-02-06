from argparse import ArgumentParser
from c42sec.profile import profile
from c42sec.send_to import send_to
from c42sec.write_to import write_to


def main():
    c42sec_arg_parser = ArgumentParser()
    subcommand_parser = c42sec_arg_parser.add_subparsers()
    _init_subcommands(subcommand_parser)
    args = c42sec_arg_parser.parse_args()
    _call(args, c42sec_arg_parser.print_help)


def _init_subcommands(subcommand_parser):
    profile.init(subcommand_parser)
    send_to.init(subcommand_parser)
    write_to.init(subcommand_parser)


def _call(args, print_help):
    """Call provided subcommand with args."""
    try:
        args.func(args)
    except AttributeError as err:
        if str(err) == "'Namespace' object has no attribute 'func'":
            print_help()
        else:
            print(err)


if __name__ == "__main__":
    main()
