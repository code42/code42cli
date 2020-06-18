from getpass import getpass

import click

import code42cli.profile as cliprofile
from code42cli.compat import str
from code42cli.profile import print_and_log_no_existing_profile
from code42cli.sdk_client import validate_connection
from code42cli.util import does_user_agree
from code42cli.logger import get_main_cli_logger


@click.group()
def profile():
    """For managing Code42 settings."""
    pass


profile_name_arg = click.argument("profile_name", required=False)
name_option = click.option(
    "-n",
    "--name",
    required=True,
    type=str,
    help="The name of the Code42 CLI profile to use when executing this command.",
)
server_option = click.option(
    "-s", "--server", required=True, type=str, help="The url and port of the Code42 server."
)
username_option = click.option(
    "-u", "--username", required=True, type=str, help="The username of the Code42 API user."
)
disable_ssl_option = click.option(
    "--disable-ssl-errors",
    is_flag=True,
    help="For development purposes, do not validate the SSL certificates of Code42 servers. "
    "This is not recommended unless it is required.",
)


@profile.command()
@profile_name_arg
def show(profile_name):
    """Print the details of a profile."""
    c42profile = cliprofile.get_profile(profile_name)
    logger = get_main_cli_logger()
    logger.print_info(u"\n{0}:".format(c42profile.name))
    logger.print_info(u"\t* username = {}".format(c42profile.username))
    logger.print_info(u"\t* authority url = {}".format(c42profile.authority_url))
    logger.print_info(u"\t* ignore-ssl-errors = {}".format(c42profile.ignore_ssl_errors))
    if cliprofile.get_stored_password(c42profile.name) is not None:
        logger.print_info(u"\t* A password is set.")
    logger.print_info(u"")


@profile.command()
@name_option
@server_option
@username_option
@disable_ssl_option
def create(name, server, username, disable_ssl_errors=False):
    """Create profile settings. The first profile created will be the default."""
    cliprofile.create_profile(name, server, username, disable_ssl_errors)
    _prompt_for_allow_password_set(name)
    get_main_cli_logger().print_info(u"Successfully created profile '{}'.".format(name))


@profile.command()
@name_option
@server_option
@username_option
@disable_ssl_option
def update(name=None, server=None, username=None, disable_ssl_errors=None):
    """Update an existing profile."""
    profile = cliprofile.get_profile(name)
    cliprofile.update_profile(profile.name, server, username, disable_ssl_errors)
    _prompt_for_allow_password_set(profile.name)
    get_main_cli_logger().print_info(u"Profile '{}' has been updated.".format(profile.name))


@profile.command()
@profile_name_arg
def reset_pw(profile_name=None):
    """Change the stored password for a profile."""
    c42profile = cliprofile.get_profile(profile_name)
    new_password = getpass()
    _validate_connection(c42profile.authority_url, c42profile.username, new_password)
    cliprofile.set_password(new_password, c42profile.name)


def _validate_connection(authority, username, password):
    if not validate_connection(authority, username, password):
        logger = get_main_cli_logger()
        logger.print_and_log_error(
            u"Your credentials failed to validate, so your password was not stored."
            u"Check your network connection and the spelling of your username and server URL."
        )
        exit(1)


@profile.command("list")
def _list():
    """Show all existing stored profiles."""
    profiles = cliprofile.get_all_profiles()
    logger = get_main_cli_logger()
    if not profiles:
        print_and_log_no_existing_profile()
        return
    for profile in profiles:
        logger.print_info(str(profile))


@profile.command()
@profile_name_arg
def use(profile_name):
    """Set a profile as the default."""
    cliprofile.switch_default_profile(profile_name)


@profile.command()
@profile_name_arg
def delete(profile_name):
    """Deletes a profile and its stored password (if any)."""
    logger = get_main_cli_logger()
    if cliprofile.is_default_profile(profile_name):
        logger.print_info(u"\n{} is currently the default profile!".format(profile_name))
    if not does_user_agree(
        u"\nDeleting this profile will also delete any stored passwords and checkpoints. "
        u"Are you sure? (y/n): "
    ):
        return
    cliprofile.delete_profile(profile_name)


@profile.command()
def delete_all():
    """Deletes all profiles and saved passwords (if any)."""
    existing_profiles = cliprofile.get_all_profiles()
    logger = get_main_cli_logger()
    if existing_profiles:
        logger.print_info(u"\nAre you sure you want to delete the following profiles?")
        for profile in existing_profiles:
            logger.print_info(u"\t{}".format(profile.name))
        if does_user_agree(
            u"\nThis will also delete any stored passwords and checkpoints. (y/n): "
        ):
            for profile in existing_profiles:
                cliprofile.delete_profile(profile.name)
    else:
        logger.print_info(u"\nNo profiles exist. Nothing to delete.")


def _prompt_for_allow_password_set(profile_name):
    if does_user_agree(u"Would you like to set a password? (y/n): "):
        reset_pw(profile_name)
