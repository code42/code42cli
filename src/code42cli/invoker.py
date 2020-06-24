import re

import click
import difflib

from py42.exceptions import Py42HTTPError, Py42ForbiddenError

from code42cli.logger import get_main_cli_logger
from code42cli.errors import LoggedCLIError

_DIFFLIB_CUT_OFF = 0.6


class ExceptionHandlingGroup(click.Group):
    logger = get_main_cli_logger()
    _original_args = None

    def make_context(self, info_name, args, parent=None, **extra):

        # grab the original command line arguments for logging
        self._original_args = " ".join(args)

        return super().make_context(info_name, args, parent=parent, **extra)

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except click.UsageError as err:
            self._suggest_cmd(err)
        except click.ClickException as err:
            self.logger.log_error(str(err))
            raise
        except Py42ForbiddenError as err:
            self.logger.log_verbose_error(self._original_args, err.response.request)
            self.logger.print_and_log_permissions_error()
            raise LoggedCLIError("no perms")
            # self.logger.print_errors_occurred_message()
        except Py42HTTPError as err:
            self.logger.log_verbose_error(self._original_args, err.response.request)
            self.logger.print_errors_occurred_message()

    @staticmethod
    def _suggest_cmd(usage_err):
        """Handles fuzzy suggestion of commands that are close to the bad command entered."""
        if usage_err.message is not None:
            match = re.match("No such command '(.*)'.", usage_err.message)
            if match:
                bad_arg = match.groups()[0]
                available_commands = list(usage_err.ctx.command.commands.keys())
                suggested_commands = difflib.get_close_matches(
                    bad_arg, available_commands, cutoff=_DIFFLIB_CUT_OFF
                )
                if not suggested_commands:
                    raise usage_err
                usage_err.message = "No such command '{}'. Did you mean {}?".format(
                    bad_arg, " or ".join(suggested_commands)
                )
        raise usage_err
