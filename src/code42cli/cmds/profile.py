from __future__ import print_function

from getpass import getpass

import code42cli.profile as cliprofile
from code42cli.args import PROFILE_HELP
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
        arg_customizer=_load_profile_description,
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
        arg_customizer=_load_profile_description,
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
        u"{} {}".format(usage_prefix, u"update <profile-name> -s <server-address> -u <username>"),
        handler=update_profile,
        arg_customizer=_load_profile_update_descriptions,
    )

    return [show, list_all, use, reset_pw, create, update]


def show_profile(profile=None):
    """Prints the given profile to stdout."""
    c42profile = cliprofile.get_profile(profile)
    print(u"\n{0}:".format(c42profile.name))
    print(u"\t* username = {}".format(c42profile.username))
    print(u"\t* authority url = {}".format(c42profile.authority_url))
    print(u"\t* ignore-ssl-errors = {}".format(c42profile.ignore_ssl_errors))
    if cliprofile.get_stored_password(c42profile.name) is not None:
        print(u"\t* A password is set.")
    print(u"")


def create_profile(profile, server, username, disable_ssl_errors=False):
    """Sets the given profile using command line arguments."""
    if cliprofile.profile_exists(profile):
        print_error(u"A profile named {} already exists.".format(profile))
        exit(1)

    cliprofile.create_profile(profile, server, username, disable_ssl_errors)
    _prompt_for_allow_password_set(profile)


def update_profile(profile=None, server=None, username=None, disable_ssl_errors=None):
    profile = cliprofile.get_profile(profile)
    if profile.has_stored_password:
        _validate_connection(server, username, profile.get_password())
    cliprofile.update_profile(profile, server, username, disable_ssl_errors)
    if does_user_agree(u"Would you like to store this password? (y/n): "):
        new_password = getpass()
        cliprofile.set_password(new_password, profile)


def prompt_for_password_reset(profile=None):
    """Securely prompts for your password and then stores it using keyring."""
    c42profile = cliprofile.get_profile(profile)
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


def _load_profile_description(argument_collection):
    profile = argument_collection.arg_configs["profile"]
    profile.set_help(PROFILE_HELP)


def _load_profile_create_descriptions(argument_collection):
    profile = argument_collection.arg_configs["profile"]
    profile.set_help(u"The name to give the profile being created.")
    _load_profile_settings_descriptions(argument_collection)


def _load_profile_update_descriptions(argument_collection):
    profile = argument_collection.arg_configs["profile"]
    profile.set_help(u"The name to give the profile being updated.")
    _load_profile_settings_descriptions(argument_collection)


def _load_profile_settings_descriptions(argument_collection):
    server = argument_collection.arg_configs["server"]
    username = argument_collection.arg_configs["username"]
    disable_ssl_errors = argument_collection.arg_configs["disable_ssl_errors"]
    server.set_help(u"The url and port of the Code42 server.")
    username.set_help(u"The username of the Code42 API user.")
    disable_ssl_errors.set_help(
        u"For development purposes, do not validate the SSL certificates of Code42 servers."
        u"This is not recommended unless it is required."
    )


def _prompt_for_allow_password_set(profile_name):
    if does_user_agree(u"Would you like to set a password? (y/n): "):
        prompt_for_password_reset(profile_name)
