from c42sec._internal.cursor_store import AEDCursorStore


def init(subcommand_parser):
    parser = subcommand_parser.add_parser("clear-checkpoint")
    parser.set_defaults(func=clear_checkpoint)


def clear_checkpoint(*args):
    AEDCursorStore().reset()


if __name__ == "__main__":
    clear_checkpoint()
