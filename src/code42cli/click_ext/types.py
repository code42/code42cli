import click


class FileOrString(click.File):
    """Declares a parameter to be a file (if the argument begins with `@`), otherwise accepts it as
    a string.
    """

    def __init__(self):
        super().__init__("r")

    def convert(self, value, param, ctx):
        if value.startswith("@") or value == "-":
            value = value.lstrip("@")
            file = super().convert(value, param, ctx)
            return file.read()
        else:
            return value
