import py42.sdk
import py42.settings
import py42.settings.debug as debug
import requests
from click import prompt
from click import secho
from py42.exceptions import Py42MFARequiredError
from py42.exceptions import Py42UnauthorizedError
from requests.exceptions import ConnectionError
from requests.exceptions import SSLError

from code42cli.errors import Code42CLIError
from code42cli.errors import LoggedCLIError
from code42cli.logger import get_main_cli_logger

py42.settings.items_per_page = 500

logger = get_main_cli_logger()


def create_sdk(profile, is_debug_mode, password=None, totp=None):
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
    password = password or profile.get_password()
    return validate_connection(profile.authority_url, profile.username, password, totp)


def validate_connection(authority_url, username, password, totp=None):
    try:
        return py42.sdk.from_local_account(authority_url, username, password, totp=totp)
    except SSLError as err:
        logger.log_error(str(err))
        raise LoggedCLIError(
            f"Problem connecting to {authority_url}, SSL certificate verification failed.\nUpdate profile with --disable-ssl-errors to bypass certificate checks (not recommended!)."
        )
    except ConnectionError as err:
        logger.log_error(str(err))
        raise LoggedCLIError(f"Problem connecting to {authority_url}.")
    except Py42MFARequiredError:
        totp = prompt("Multi-factor authentication required. Enter TOTP", type=int)
        return validate_connection(authority_url, username, password, totp)
    except Py42UnauthorizedError as err:
        logger.log_error(str(err))
        if "INVALID_TIME_BASED_ONE_TIME_PASSWORD" in err.response.text:
            raise Code42CLIError(f"Invalid TOTP token for user {username}.")
        else:
            raise Code42CLIError(f"Invalid credentials for user {username}.")
    except Exception as err:
        logger.log_error(str(err))
        raise LoggedCLIError("Unknown problem validating connection.")
