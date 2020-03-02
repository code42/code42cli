from code42cli.securitydata.cursor_store import AEDCursorStore


def init(subcommand_parser):
    """Sets up the `clear-checkpoint` subcommand for cleared the stored checkpoint for `incremental` mode.
        Args:
            subcommand_parser: The subparsers group created by the parent parser.
    """
    parser = subcommand_parser.add_parser("clear-checkpoint")
    parser.set_defaults(func=clear_checkpoint)


def clear_checkpoint(*args):
    """Removes the stored checkpoint that keeps track of the last event you got.
        To use, run `code42 clear-checkpoint`.
        This affects `incremental` mode by causing it to behave like it has never been run before.
    """
    AEDCursorStore().reset()


if __name__ == "__main__":
    clear_checkpoint()
