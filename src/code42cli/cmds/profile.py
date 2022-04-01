from getpass import getpass

import click
from click import echo
from click import secho

import code42cli.profile as cliprofile
from code42cli.click_ext.types import PromptChoice
from code42cli.click_ext.types import TOTP
from code42cli.errors import Code42CLIError
from code42cli.options import yes_option
from code42cli.profile import CREATE_PROFILE_HELP
from code42cli.sdk_client import create_sdk
from code42cli.util import does_user_agree


@click.group()
def profile():
    """Manage Code42 connection settings."""
    pass


debug_option = click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Turn on debug logging.",
)
totp_option = click.option(
    "--totp", help="TOTP token for multi-factor authentication.", type=TOTP()
)


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
    echo(f"\n{c42profile.name}:")
    echo(f"\t* username = {c42profile.username}")
    echo(f"\t* authority url = {c42profile.authority_url}")
    echo(f"\t* ignore-ssl-errors = {c42profile.ignore_ssl_errors}")
    if cliprofile.get_stored_password(c42profile.name) is not None:
        echo("\t* A password is set.")
    echo("")
    echo("")


@profile.command()
@name_option(required=True)
@server_option(required=True)
@username_option(required=True)
@password_option
@totp_option
@yes_option(hidden=True)
@disable_ssl_option
@debug_option
def create(name, server, username, password, disable_ssl_errors, debug, totp):
    """Create profile settings. The first profile created will be the default."""
    cliprofile.create_profile(name, server, username, disable_ssl_errors)
    password = password or _prompt_for_password(name)
    if password:
        _set_pw(name, password, debug, totp=totp)
    echo(f"Successfully created profile '{name}'.")


@profile.command()
@name_option()
@server_option()
@username_option()
@password_option
@totp_option
@disable_ssl_option
@debug_option
def update(name, server, username, password, disable_ssl_errors, debug, totp):
    """Update an existing profile."""
    c42profile = cliprofile.get_profile(name)

    if not server and not username and not password and disable_ssl_errors is None:
        raise click.UsageError(
            "Must provide at least one of `--username`, `--server`, `--password`, or "
            "`--disable-ssl-errors` when updating a profile."
        )

    cliprofile.update_profile(c42profile.name, server, username, disable_ssl_errors)
    if not password and not c42profile.has_stored_password:
        password = _prompt_for_password(c42profile.name)
    if password:
        _set_pw(name, password, debug, totp=totp)

    echo(f"Profile '{c42profile.name}' has been updated.")


@profile.command()
@profile_name_arg()
@debug_option
def reset_pw(profile_name, debug):
    """\b
    Change the stored password for a profile. Only affects what's stored in the local profile,
    does not make any changes to the Code42 user account."""
    password = getpass()
    profile_name_saved = _set_pw(profile_name, password, debug)
    echo(f"Password updated for profile '{profile_name_saved}'.")


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
    """\b
    Set a profile as the default. If not providing a profile-name,
    prompts for a choice from a list of all profiles."""

    if not profile_name:
        _select_profile_from_prompt()
        return

    _set_default_profile(profile_name)


@profile.command()
@yes_option()
@profile_name_arg(required=True)
def delete(profile_name):
    """Deletes a profile and its stored password (if any)."""
    try:
        cliprofile.get_profile(profile_name)
    except Code42CLIError:
        raise Code42CLIError(f"Profile '{profile_name}' does not exist.")
    message = (
        "\nDeleting this profile will also delete any stored passwords and checkpoints. "
        "Are you sure? (y/n): "
    )
    if cliprofile.is_default_profile(profile_name):
        message = f"\n'{profile_name}' is currently the default profile!\n{message}"
    if does_user_agree(message):
        cliprofile.delete_profile(profile_name)
        echo(f"Profile '{profile_name}' has been deleted.")


@profile.command()
@yes_option()
def delete_all():
    """Deletes all profiles and saved passwords (if any)."""
    existing_profiles = cliprofile.get_all_profiles()
    if existing_profiles:
        profile_str_list = "\n\t".join(
            [c42profile.name for c42profile in existing_profiles]
        )
        message = (
            f"\nAre you sure you want to delete the following profiles?\n\t{profile_str_list}"
            "\n\nThis will also delete any stored passwords and checkpoints. (y/n): "
        )
        if does_user_agree(message):
            for profile_obj in existing_profiles:
                cliprofile.delete_profile(profile_obj.name)
                echo(f"Profile '{profile_obj.name}' has been deleted.")
    else:
        echo("\nNo profiles exist. Nothing to delete.")


def _prompt_for_password(profile_name):
    if does_user_agree("Would you like to set a password? (y/n): "):
        password = getpass()
        return password


def _set_pw(profile_name, password, debug, totp=None):
    c42profile = cliprofile.get_profile(profile_name)
    try:
        create_sdk(c42profile, is_debug_mode=debug, password=password, totp=totp)
    except Exception:
        secho("Password not stored!", bold=True)
        raise
    cliprofile.set_password(password, c42profile.name)
    return c42profile.name


def _select_profile_from_prompt():
    """Set the default profile from user input."""
    profiles = cliprofile.get_all_profiles()
    profile_names = [profile_choice.name for profile_choice in profiles]
    choices = PromptChoice(profile_names)
    choices.print_choices()
    prompt_message = "Input the number of the profile you wish to use"
    profile_name = click.prompt(prompt_message, type=choices)
    _set_default_profile(profile_name)


def _set_default_profile(profile_name):
    cliprofile.switch_default_profile(profile_name)
    _print_default_profile_was_set(profile_name)


def _print_default_profile_was_set(profile_name):
    echo(f"{profile_name} has been set as the default profile.")
