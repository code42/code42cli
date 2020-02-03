from argparse import ArgumentParser
from c42sec.profile import profile


def main():
    c42sec_arg_parser = ArgumentParser()
    profile.init(c42sec_arg_parser)
    args = c42sec_arg_parser.parse_args()

    # Call which ever subcommand was given.
    _call(args, c42sec_arg_parser.print_help)


def _call(args, print_help):
    try:
        args.func(args)
    except AttributeError:
        print_help()


if __name__ == "__main__":
    main()
