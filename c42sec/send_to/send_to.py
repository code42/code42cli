

def init(parent_parser):
    subparsers = parent_parser.add_subparsers()
    write_to_parser = subparsers.add_parser("write-to")
