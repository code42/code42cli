import difflib
import re

import click
from click._compat import get_text_stderr
from py42.exceptions import Py42ForbiddenError
from py42.exceptions import Py42HTTPError
from py42.exceptions import Py42InvalidRuleOperationError
from py42.exceptions import Py42LegalHoldNotFoundOrPermissionDeniedError
from py42.exceptions import Py42UserAlreadyAddedError

from code42cli.logger import get_main_cli_logger
from code42cli.logger import get_view_error_details_message

ERRORED = False
_DIFFLIB_CUT_OFF = 0.6


class Code42CLIError(click.ClickException):
    """Base CLI exception. The `message` param automatically gets logged to error file and printed
    to stderr in red text. If `help` param is provided, it will also be printed to stderr after the
    message but not logged to file.
    """

    def __init__(self, message, help=None):
        self.help = help
        super().__init__(message)

    def show(self, file=None):
        """Override default `show` to print CLI errors in red text."""
        if file is None:
            file = get_text_stderr()
        click.secho("Error: {}".format(self.format_message()), file=file, fg="red")
        if self.help:
            click.echo(self.help, err=True)


class LoggedCLIError(Code42CLIError):
    """Exception to be raised when wanting to point users to error logs for error details.

    If `message` param is provided it will be printed to screen along with message on where to
    find error details in the log.
    """

    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

    def format_message(self):
        locations_message = get_view_error_details_message()
        return (
            "{}\n{}".format(self.message, locations_message)
            if self.message
            else locations_message
        )


class UserDoesNotExistError(Code42CLIError):
    """An error to represent a username that is not in our system. The CLI shows this error when
    the user tries to add or remove a user that does not exist. This error is not shown during
    bulk add or remove."""

    def __init__(self, username):
        super().__init__("User '{}' does not exist.".format(username))


class UserNotInLegalHoldError(Code42CLIError):
    def __init__(self, username, matter_id):
        super().__init__(
            "User '{}' is not an active member of legal hold matter '{}'.".format(
                username, matter_id
            )
        )


class ExceptionHandlingGroup(click.Group):
    """Custom click.Group subclass to add custom exception handling."""

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
