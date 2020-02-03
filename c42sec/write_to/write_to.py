def init(subcommand_parser):
    write_to_parser = subcommand_parser.add_parser("write-to")
    write_to_parser.set_defaults(func=write_to)


def write_to(args):
    print("Send to called")
