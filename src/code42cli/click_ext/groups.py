import difflib
import platform
import re
from collections import OrderedDict

import click
from py42.exceptions import Py42ActiveLegalHoldError
from py42.exceptions import Py42CaseAlreadyHasEventError
from py42.exceptions import Py42CaseNameExistsError
from py42.exceptions import Py42CloudAliasCharacterLimitExceededError
from py42.exceptions import Py42CloudAliasLimitExceededError
from py42.exceptions import Py42DescriptionLimitExceededError
from py42.exceptions import Py42ForbiddenError
from py42.exceptions import Py42HTTPError
from py42.exceptions import Py42InvalidEmailError
from py42.exceptions import Py42InvalidPasswordError
from py42.exceptions import Py42InvalidRuleOperationError
from py42.exceptions import Py42InvalidUsernameError
from py42.exceptions import Py42LegalHoldNotFoundOrPermissionDeniedError
from py42.exceptions import Py42OrgNotFoundError
from py42.exceptions import Py42TrustedActivityConflictError
from py42.exceptions import Py42TrustedActivityIdNotFound
from py42.exceptions import Py42TrustedActivityInvalidCharacterError
from py42.exceptions import Py42UpdateClosedCaseError
from py42.exceptions import Py42UserAlreadyAddedError
from py42.exceptions import Py42UsernameMustBeEmailError
from py42.exceptions import Py42UserNotOnListError

from code42cli.errors import Code42CLIError
from code42cli.errors import LoggedCLIError
from code42cli.errors import UserDoesNotExistError
from code42cli.logger import get_main_cli_logger
from code42cli.logger.handlers import SyslogServerNetworkConnectionError

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
            SyslogServerNetworkConnectionError,
            Py42CaseNameExistsError,
            Py42DescriptionLimitExceededError,
            Py42CaseAlreadyHasEventError,
            Py42UpdateClosedCaseError,
            Py42UsernameMustBeEmailError,
            Py42InvalidEmailError,
            Py42InvalidPasswordError,
            Py42InvalidUsernameError,
            Py42ActiveLegalHoldError,
            Py42OrgNotFoundError,
            Py42TrustedActivityConflictError,
            Py42TrustedActivityInvalidCharacterError,
            Py42TrustedActivityIdNotFound,
            Py42CloudAliasLimitExceededError,
            Py42CloudAliasCharacterLimitExceededError,
        ) as err:
            msg = err.args[0]
            self.logger.log_error(msg)
            raise Code42CLIError(msg)

        except Py42ForbiddenError as err:
            self.logger.log_verbose_error(self._original_args, err.response.request)
            raise LoggedCLIError(
                "You do not have the necessary permissions to perform this task. "
                "Try using or creating a different profile."
            )

        except Py42HTTPError as err:
            self.logger.log_verbose_error(self._original_args, err.response.request)
            raise LoggedCLIError("Problem making request to server.")

        except UnicodeEncodeError:
            if platform.system() == "Windows":
                cmd = 'if using powershell: $ENV:PYTHONIOENCODING="utf-16"\nif using cmd.exe:    SET PYTHONIOENCODING="utf-16"'
            else:
                cmd = 'export PYTHONIOENCODING="utf-8"'
            raise Code42CLIError(
                f"Failed to handle unicode character using environment's detected encoding, try running the following:\n\n{cmd}\n\nand then re-run your `code42` command."
            )

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
                usage_err.message = (
                    f"No such command '{bad_arg}'. "
                    f"Did you mean {' or '.join(suggested_commands)}?"
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


class ExtensionGroup(ExceptionHandlingGroup):
    """A helper click.Group for extension scripts. If only a single command is added to this group,
    that command will be the "default" and won't need to be explicitly passed as the first argument
    to the extension script.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_args(self, ctx, args):
        if len(self.commands) == 1:
            cmd_name, cmd = next(iter(self.commands.items()))
            if not args or args[0] not in self.commands:
                self.commands = {"": cmd}
                args.insert(0, "")
        super().parse_args(ctx, args)
