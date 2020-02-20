def init(subcommand_parser):
    send_to_parser = subcommand_parser.add_parser("send-to")
    send_to_parser.set_defaults(func=send_to)


def send_to(args):
    print("Send to called")
