from os import environ

import py42.sdk
import py42.settings
import py42.settings.debug as debug
import requests
from click import prompt
from click import secho
from py42.exceptions import Py42UnauthorizedError
from requests.exceptions import ConnectionError
from requests.exceptions import SSLError

from code42cli.click_ext.types import TOTP
from code42cli.errors import Code42CLIError
from code42cli.errors import LoggedCLIError
from code42cli.logger import get_main_cli_logger

py42.settings.items_per_page = 500

logger = get_main_cli_logger()


def create_sdk(profile, is_debug_mode, password=None, totp=None, api_client=False):
    proxy = environ.get("HTTPS_PROXY") or environ.get("https_proxy")
    if proxy:
        py42.settings.proxies = {"https": proxy}
    if is_debug_mode:
        py42.settings.debug.level = debug.DEBUG
    if profile.ignore_ssl_errors == "True":
        secho(
            f"Warning: Profile '{profile.name}' has SSL verification disabled. "
            "Adding certificate verification is strongly advised.",
            fg="red",
            err=True,
        )
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )
        py42.settings.verify_ssl_certs = False
    password = password or profile.get_password()
    return _validate_connection(
        profile.authority_url, profile.username, password, totp, api_client
    )


def _validate_connection(
    authority_url, username, password, totp=None, api_client=False
):
    try:
        if api_client:
            return py42.sdk.from_api_client(authority_url, username, password)
        return py42.sdk.from_local_account(authority_url, username, password, totp=totp)
    except SSLError as err:
        logger.log_error(err)
        raise LoggedCLIError(
            f"Problem connecting to {authority_url}, SSL certificate verification failed.\nUpdate profile with --disable-ssl-errors to bypass certificate checks (not recommended!)."
        )
    except ConnectionError as err:
        logger.log_error(err)
        if "ProxyError" in str(err):
            raise LoggedCLIError(
                f"Unable to connect to proxy! Proxy configuration set by environment variable: HTTPS_PROXY={environ.get('HTTPS_PROXY')}"
            )
        raise LoggedCLIError(f"Problem connecting to {authority_url}.")
    except Py42UnauthorizedError as err:
        logger.log_error(err)
        if "LoginConfig: LOCAL_2FA" in str(err):
            if totp is None:
                totp = prompt(
                    "Multi-factor authentication required. Enter TOTP", type=TOTP()
                )
                return _validate_connection(authority_url, username, password, totp)
            else:
                raise Code42CLIError(
                    f"Invalid credentials or TOTP token for user {username}."
                )
        else:
            raise Code42CLIError(f"Invalid credentials for user {username}.")
    except Exception as err:
        logger.log_error(err)
        raise LoggedCLIError("Unknown problem validating connection.")
