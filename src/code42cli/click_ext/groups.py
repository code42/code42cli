import difflib
import re
from collections import OrderedDict

import click
from py42.exceptions import Py42ForbiddenError
from py42.exceptions import Py42HTTPError
from py42.exceptions import Py42InvalidRuleOperationError
from py42.exceptions import Py42LegalHoldNotFoundOrPermissionDeniedError
from py42.exceptions import Py42UserAlreadyAddedError
from py42.exceptions import Py42UserNotOnListError

from code42cli.errors import Code42CLIError
from code42cli.errors import LoggedCLIError
from code42cli.errors import UserDoesNotExistError
from code42cli.logger import get_main_cli_logger

_DIFFLIB_CUT_OFF = 0.6


class ExceptionHandlingGroup(click.Group):
    """A `click.Group` subclass to add custom exception handling."""

    logger = get_main_cli_logger()
    _original_args = None

    def make_context(self, info_name, args, parent=None, **extra):

        # grab the original command line arguments for logging purposes
        self._original_args = " ".join(args)

        return super().make_context(info_name, args, parent=parent, **extra)

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)

        except click.UsageError as err:
            self._suggest_cmd(err)

        except LoggedCLIError:
            raise

        except Code42CLIError as err:
            self.logger.log_error(str(err))
            raise

        except click.ClickException:
            raise

        except click.exceptions.Exit:
            raise

        except (
            UserDoesNotExistError,
            Py42UserAlreadyAddedError,
            Py42UserNotOnListError,
            Py42InvalidRuleOperationError,
            Py42LegalHoldNotFoundOrPermissionDeniedError,
        ) as err:
            self.logger.log_error(err)
            raise Code42CLIError(str(err))

        except Py42ForbiddenError as err:
            self.logger.log_verbose_error(self._original_args, err.response.request)
            raise LoggedCLIError(
                "You do not have the necessary permissions to perform this task. "
                "Try using or creating a different profile."
            )

        except Py42HTTPError as err:
            self.logger.log_verbose_error(self._original_args, err.response.request)
            raise LoggedCLIError("Problem making request to server.")

        except OSError:
            raise

        except Exception:
            self.logger.log_verbose_error()
            raise LoggedCLIError("Unknown problem occurred.")

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


class OrderedGroup(click.Group):
    """A `click.Group` subclass that uses an `OrderedDict` to store commands so the help text lists
    them in the order they were defined/added to the group.
    """

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        # the registered subcommands by their exported names.
        self.commands = commands or OrderedDict()

    def list_commands(self, ctx):
        return self.commands
