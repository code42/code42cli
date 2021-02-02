import click

from code42cli.errors import Code42CLIError
from code42cli.logger import get_logger_for_server
from code42cli.output_formats import OutputFormat


def _try_get_logger_for_server(hostname, protocol, output_format, certs):
    try:
        return get_logger_for_server(hostname, protocol, output_format, certs)
    except Exception as err:
        raise Code42CLIError(
            "Unable to connect to {}. Failed with error: {}.".format(hostname, str(err))
        )


class SendToCommand(click.Command):
    def invoke(self, ctx):
        certs = ctx.params.get("certs")
        hostname = ctx.params.get("hostname")
        protocol = ctx.params.get("protocol")
        output_format = ctx.params.get("format", OutputFormat.RAW)
        ignore_cert_validation = ctx.params.get("ignore_cert_validation")
        if ignore_cert_validation:
            certs = "ignore"

        ctx.obj.logger = _try_get_logger_for_server(
            hostname, protocol, output_format, certs
        )
        return super().invoke(ctx)
