from getpass import getpass

import click
from click import echo
from click import secho
from py42.exceptions import Py42MFARequiredError

import code42cli.profile as cliprofile
from code42cli.errors import Code42CLIError
from code42cli.options import yes_option
from code42cli.profile import CREATE_PROFILE_HELP
from code42cli.sdk_client import create_sdk
from code42cli.util import does_user_agree


@click.group()
def profile():
    """Manage Code42 connection settings."""
    pass


def profile_name_arg(required=False):
    return click.argument("profile_name", required=required)


def name_option(required=False):
    return click.option(
        "-n",
        "--name",
        required=required,
        help="The name of the Code42 CLI profile to use when executing this command.",
    )


def server_option(required=False):
    return click.option(
        "-s",
        "--server",
        required=required,
        help="The URL you use to sign into Code42.",
    )


def username_option(required=False):
    return click.option(
        "-u",
        "--username",
        required=required,
        help="The username of the Code42 API user.",
    )


password_option = click.option(
    "--password",
    help="The password for the Code42 API user. If this option is omitted, interactive prompts "
    "will be used to obtain the password.",
)

disable_ssl_option = click.option(
    "--disable-ssl-errors",
    is_flag=True,
    help="For development purposes, do not validate the SSL certificates of Code42 servers. "
    "This is not recommended, except for specific scenarios like testing.",
    default=None,
)


@profile.command()
@profile_name_arg()
def show(profile_name):
    """Print the details of a profile."""
    c42profile = cliprofile.get_profile(profile_name)
    echo("\n{}:".format(c42profile.name))
    echo("\t* username = {}".format(c42profile.username))
    echo("\t* authority url = {}".format(c42profile.authority_url))
    echo("\t* ignore-ssl-errors = {}".format(c42profile.ignore_ssl_errors))
    if cliprofile.get_stored_password(c42profile.name) is not None:
        echo("\t* A password is set.")
    echo("")
    echo("")


@profile.command()
@name_option(required=True)
@server_option(required=True)
@username_option(required=True)
@password_option
@yes_option(hidden=True)
@disable_ssl_option
def create(name, server, username, password, disable_ssl_errors):
    """Create profile settings. The first profile created will be the default."""
    cliprofile.create_profile(name, server, username, disable_ssl_errors)
    if password:
        _set_pw(name, password)
    else:
        _prompt_for_allow_password_set(name)
    echo("Successfully created profile '{}'.".format(name))


@profile.command()
@name_option()
@server_option()
@username_option()
@password_option
@disable_ssl_option
def update(name, server, username, password, disable_ssl_errors):
    """Update an existing profile."""
    c42profile = cliprofile.get_profile(name)

    if not server and not username and not password and disable_ssl_errors is None:
        raise click.UsageError(
            "Must provide at least one of `--username`, `--server`, `--password`, or "
            "`--disable-ssl-errors` when updating a profile."
        )

    cliprofile.update_profile(c42profile.name, server, username, disable_ssl_errors)
    if password:
        _set_pw(name, password)
    elif not c42profile.has_stored_password:
        _prompt_for_allow_password_set(c42profile.name)

    echo("Profile '{}' has been updated.".format(c42profile.name))


@profile.command()
@profile_name_arg()
def reset_pw(profile_name):
    """\b
    Change the stored password for a profile. Only affects what's stored in the local profile,
    does not make any changes to the Code42 user account."""
    password = getpass()
    profile_name_saved = _set_pw(profile_name, password)
    echo("Password updated for profile '{}'.".format(profile_name_saved))


@profile.command("list")
def _list():
    """Show all existing stored profiles."""
    profiles = cliprofile.get_all_profiles()
    if not profiles:
        raise Code42CLIError("No existing profile.", help=CREATE_PROFILE_HELP)
    for c42profile in profiles:
        echo(str(c42profile))


@profile.command()
@profile_name_arg()
def use(profile_name):
    """Set a profile as the default."""
    cliprofile.switch_default_profile(profile_name)
    echo("{} has been set as the default profile.".format(profile_name))


@profile.command()
@yes_option()
@profile_name_arg(required=True)
def delete(profile_name):
    """Deletes a profile and its stored password (if any)."""
    message = "\nDeleting this profile will also delete any stored passwords and checkpoints. Are you sure? (y/n): "
    if cliprofile.is_default_profile(profile_name):
        message = "\n'{}' is currently the default profile!\n{}".format(
            profile_name, message
        )
    if does_user_agree(message):
        cliprofile.delete_profile(profile_name)
        echo("Profile '{}' has been deleted.".format(profile_name))


@profile.command()
@yes_option()
def delete_all():
    """Deletes all profiles and saved passwords (if any)."""
    existing_profiles = cliprofile.get_all_profiles()
    if existing_profiles:
        message = (
            "\nAre you sure you want to delete the following profiles?\n\t{}"
            "\n\nThis will also delete any stored passwords and checkpoints. (y/n): "
        ).format("\n\t".join([c42profile.name for c42profile in existing_profiles]))
        if does_user_agree(message):
            for profile_obj in existing_profiles:
                cliprofile.delete_profile(profile_obj.name)
                echo("Profile '{}' has been deleted.".format(profile_obj.name))
    else:
        echo("\nNo profiles exist. Nothing to delete.")


def _prompt_for_allow_password_set(profile_name):
    if does_user_agree("Would you like to set a password? (y/n): "):
        password = getpass()
        _set_pw(profile_name, password)


def _set_pw(profile_name, password):
    c42profile = cliprofile.get_profile(profile_name)
    try:
        create_sdk(c42profile, is_debug_mode=False, password=password)
    except Py42MFARequiredError:
        echo(
            "Multi-factor account detected. `--totp <token>` option will be required for all code42 invocations."
        )
    except Exception:
        secho("Password not stored!", bold=True)
        raise
    cliprofile.set_password(password, c42profile.name)
    return c42profile.name
