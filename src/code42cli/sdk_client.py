import py42.sdk
import py42.settings
import py42.settings.debug as debug
import requests
from click import secho
from py42.exceptions import Py42UnauthorizedError
from requests.exceptions import ConnectionError

from code42cli.errors import Code42CLIError
from code42cli.errors import LoggedCLIError
from code42cli.logger import get_main_cli_logger

py42.settings.items_per_page = 500

logger = get_main_cli_logger()


def create_sdk(profile, is_debug_mode):
    if is_debug_mode:
        py42.settings.debug.level = debug.DEBUG
    if profile.ignore_ssl_errors == "True":
        secho(
            "Warning: Profile '{}' has SSL verification disabled. Adding certificate verification "
            "is strongly advised.".format(profile.name),
            fg="red",
            err=True,
        )
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )
        py42.settings.verify_ssl_certs = False
    password = profile.get_password()
    return validate_connection(profile.authority_url, profile.username, password)


def validate_connection(authority_url, username, password):
    try:
        return py42.sdk.from_local_account(authority_url, username, password)
    except ConnectionError as err:
        logger.log_error(str(err))
        raise LoggedCLIError("Problem connecting to {}".format(authority_url))
    except Py42UnauthorizedError as err:
        logger.log_error(str(err))
        raise Code42CLIError("Invalid credentials for user {}".format(username))
    except Exception as err:
        logger.log_error(str(err))
        raise LoggedCLIError("Unknown problem validating connection.")
