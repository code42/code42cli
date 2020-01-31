from argparse import ArgumentParser
from c42sec.subcommands import profile


def main():
    c42sec_arg_parser = ArgumentParser()
    profile.init(c42sec_arg_parser)
    args = c42sec_arg_parser.parse_args()

    # Call which ever subcommand was given.
    _call(args)


def _call(args):
    try:
        args.func(args)
    except AttributeError:
        pass


if __name__ == "__main__":
    main()
