import json
import re

import click


class JSONFileOrString(click.File):
    """Declares a parameter to be either a JSON string or a path to a file containing parsable
    JSON.

    If the argument's first non-whitespace character is a "{", assumes it's JSON and tries to parse
    it, otherwise assumes it's a filename and tries to open file then parse contents as JSON.
    """

    def __init__(self):
        super().__init__("r")

    def convert(self, value, param, ctx):
        if re.match(
            r"\s*\{", value
        ):  # assume JSON string since it begins with a bracket
            try:
                return json.loads(value)
            except json.JSONDecodeError as decode_error:
                raise click.BadParameter(
                    "Unable to parse JSON string argument, decode error: {error}".format(
                        error=decode_error
                    )
                )
        else:
            file = super().convert(value, param, ctx)
            try:
                return json.loads(file.read())
            except json.JSONDecodeError as decode_error:
                raise click.BadParameter(
                    "Unable to parse JSON from file: {filename}, decode error: {error}".format(
                        filename=value, error=decode_error
                    )
                )
