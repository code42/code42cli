from __future__ import print_function

from getpass import getpass

import code42cli.profile as cliprofile
from code42cli.args import PROFILE_HELP, PROFILE_ARG_NAME
from code42cli.commands import Command
from code42cli.sdk_client import validate_connection
from code42cli.util import does_user_agree, print_error, print_no_existing_profile_message


def load_subcommands():
    """Sets up the `profile` subcommand with all of its subcommands."""
    usage_prefix = u"code42 profile"

    show = Command(
        u"show",
        u"Print the details of a profile.",
        u"{} {}".format(usage_prefix, u"show <optional-args>"),
        handler=show_profile,
        arg_customizer=_load_optional_profile_description,
    )

    list_all = Command(
        u"list",
        u"Show all existing stored profiles.",
        u"{} {}".format(usage_prefix, u"list"),
        handler=list_profiles,
    )

    use = Command(
        u"use",
        u"Set a profile as the default.",
        u"{} {}".format(usage_prefix, u"use <profile-name>"),
        handler=use_profile,
    )

    reset_pw = Command(
        u"reset-pw",
        u"Change the stored password for a profile.",
        u"{} {}".format(usage_prefix, u"reset-pw <optional-args>"),
        handler=prompt_for_password_reset,
        arg_customizer=_load_optional_profile_description,
    )

    create = Command(
        u"create",
        u"Create profile settings. The first profile created will be the default.",
        u"{} {}".format(usage_prefix, u"create <profile-name> <server-address> <username>"),
        handler=create_profile,
        arg_customizer=_load_profile_create_descriptions,
    )

    update = Command(
        u"update",
        u"Update an existing profile.",
        u"{} {}".format(usage_prefix, u"update <optional args>"),
        handler=update_profile,
        arg_customizer=_load_profile_update_descriptions,
    )

    delete = Command(
        u"delete",
        "Deletes a profile and its stored password (if any).",
        u"{} {}".format(usage_prefix, u"delete <profile-name>"),
        handler=delete_profile,
    )

    delete_all = Command(
        u"delete-all",
        u"Deletes all profiles and saved passwords (if any).",
        u"{} {}".format(usage_prefix, u"delete-all"),
        handler=delete_all_profiles,
    )

    return [show, list_all, use, reset_pw, create, update, delete, delete_all]


def show_profile(name=None):
    """Prints the given profile to stdout."""
    c42profile = cliprofile.get_profile(name)
    print(u"\n{0}:".format(c42profile.name))
    print(u"\t* username = {}".format(c42profile.username))
    print(u"\t* authority url = {}".format(c42profile.authority_url))
    print(u"\t* ignore-ssl-errors = {}".format(c42profile.ignore_ssl_errors))
    if cliprofile.get_stored_password(c42profile.name) is not None:
        print(u"\t* A password is set.")
    print(u"")


def create_profile(profile, server, username, disable_ssl_errors=False):
    cliprofile.create_profile(profile, server, username, disable_ssl_errors)
    _prompt_for_allow_password_set(profile)


def update_profile(name=None, server=None, username=None, disable_ssl_errors=None):
    profile = cliprofile.get_profile(name)
    cliprofile.update_profile(profile.name, server, username, disable_ssl_errors)
    _prompt_for_allow_password_set(profile.name)
    print(u"Profile '{}' has been updated.".format(profile.name))


def prompt_for_password_reset(name=None):
    """Securely prompts for your password and then stores it using keyring."""
    c42profile = cliprofile.get_profile(name)
    new_password = getpass()
    _validate_connection(c42profile.authority_url, c42profile.username, new_password)
    cliprofile.set_password(new_password, c42profile.name)


def _validate_connection(authority, username, password):
    if not validate_connection(authority, username, password):
        print_error(
            u"Your credentials failed to validate, so your password was not stored."
            u"Check your network connection and the spelling of your username and server URL."
        )
        exit(1)


def list_profiles(*args):
    """Lists all profiles that exist for this OS user."""
    profiles = cliprofile.get_all_profiles()
    if not profiles:
        print_no_existing_profile_message()
        return
    for profile in profiles:
        print(profile)


def use_profile(profile):
    """Changes the default profile to the given one."""
    cliprofile.switch_default_profile(profile)


def delete_profile(name):
    if cliprofile.is_default_profile(name):
        print(u"\n{} is currently the default profile!".format(name))
    if not does_user_agree(
        u"\nDeleting this profile will also delete any stored passwords and checkpoints. Are you sure? (y/n): "
    ):
        return
    cliprofile.delete_profile(name)


def delete_all_profiles():
    existing_profiles = cliprofile.get_all_profiles()
    if existing_profiles:
        print(u"\nAre you sure you want to delete the following profiles?")
        for profile in existing_profiles:
            print(u"\t{}".format(profile.name))
        if does_user_agree(
            u"\nThis will also delete any stored passwords and checkpoints. (y/n): "
        ):
            for profile in existing_profiles:
                cliprofile.delete_profile(profile.name)
    else:
        print(u"\nNo profiles exist. Nothing to delete.")


def _load_optional_profile_description(argument_collection):
    profile = argument_collection.arg_configs[u"name"]
    profile.add_short_option_name(u"-n")
    profile.set_help(PROFILE_HELP)


def _load_profile_create_descriptions(argument_collection):
    profile = argument_collection.arg_configs[PROFILE_ARG_NAME]
    profile.set_help(PROFILE_HELP)
    _load_profile_settings_descriptions(argument_collection)


def _load_profile_update_descriptions(argument_collection):
    _load_optional_profile_description(argument_collection)
    _load_profile_settings_descriptions(argument_collection)
    argument_collection.arg_configs[u"server"].add_short_option_name(u"-s")
    argument_collection.arg_configs[u"username"].add_short_option_name(u"-u")


def _load_profile_settings_descriptions(argument_collection):
    server = argument_collection.arg_configs[u"server"]
    username = argument_collection.arg_configs[u"username"]
    disable_ssl_errors = argument_collection.arg_configs[u"disable_ssl_errors"]
    server.set_help(u"The url and port of the Code42 server.")
    username.set_help(u"The username of the Code42 API user.")
    disable_ssl_errors.set_help(
        u"For development purposes, do not validate the SSL certificates of Code42 servers."
        u"This is not recommended unless it is required."
    )


def _prompt_for_allow_password_set(profile_name):
    if does_user_agree(u"Would you like to set a password? (y/n): "):
        prompt_for_password_reset(profile_name)
