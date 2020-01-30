from argparse import ArgumentParser
from c42sec.subcommands import profile


def main():
    c42sec_arg_parser = ArgumentParser()
    profile.init(c42sec_arg_parser)
    args = c42sec_arg_parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
