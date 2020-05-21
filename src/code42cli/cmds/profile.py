from getpass import getpass

from code42cli import MAIN_COMMAND
import code42cli.profile as cliprofile
from code42cli.compat import str
from code42cli.profile import print_and_log_no_existing_profile
from code42cli.args import PROFILE_HELP
from code42cli.commands import Command, SubcommandLoader
from code42cli.sdk_client import validate_connection
from code42cli.util import does_user_agree
from code42cli.logger import get_main_cli_logger


class ProfileSubcommandLoader(SubcommandLoader):
    SHOW = u"show"
    LIST = u"list"
    USE = u"use"
    RESET_PW = u"reset-pw"
    CREATE = u"create"
    UPDATE = u"update"
    DELETE = u"delete"
    DELETE_ALL = u"delete-all"

    def load_commands(self):
        """Sets up the `profile` subcommand with all of its subcommands."""
        usage_prefix = u"{} profile".format(MAIN_COMMAND)

        show = Command(
            self.SHOW,
            u"Print the details of a profile.",
            u"{} {}".format(usage_prefix, u"show <optional-args>"),
            handler=show_profile,
            arg_customizer=_load_optional_profile_description,
        )

        list_all = Command(
            self.LIST,
            u"Show all existing stored profiles.",
            u"{} {}".format(usage_prefix, u"list"),
            handler=list_profiles,
        )

        use = Command(
            self.USE,
            u"Set a profile as the default.",
            u"{} {}".format(usage_prefix, u"use <profile-name>"),
            handler=use_profile,
        )

        reset_pw = Command(
            self.RESET_PW,
            u"Change the stored password for a profile.",
            u"{} {}".format(usage_prefix, u"reset-pw <optional-args>"),
            handler=prompt_for_password_reset,
            arg_customizer=_load_optional_profile_description,
        )

        create = Command(
            self.CREATE,
            u"Create profile settings. The first profile created will be the default.",
            u"{} {}".format(
                usage_prefix,
                u"create --name <profile-name> --server <server-address> --username <username>",
            ),
            handler=create_profile,
            arg_customizer=_load_profile_create_descriptions,
        )

        update = Command(
            self.UPDATE,
            u"Update an existing profile.",
            u"{} {}".format(usage_prefix, u"update <optional args>"),
            handler=update_profile,
            arg_customizer=_load_profile_update_descriptions,
        )

        delete = Command(
            self.DELETE,
            u"Deletes a profile and its stored password (if any).",
            u"{} {}".format(usage_prefix, u"delete <profile-name>"),
            handler=delete_profile,
        )

        delete_all = Command(
            self.DELETE_ALL,
            u"Deletes all profiles and saved passwords (if any).",
            u"{} {}".format(usage_prefix, u"delete-all"),
            handler=delete_all_profiles,
        )

        return [show, list_all, use, reset_pw, create, update, delete, delete_all]


def show_profile(name=None):
    """Prints the given profile to stdout."""
    c42profile = cliprofile.get_profile(name)
    logger = get_main_cli_logger()
    logger.print_info(u"\n{0}:".format(c42profile.name))
    logger.print_info(u"\t* username = {}".format(c42profile.username))
    logger.print_info(u"\t* authority url = {}".format(c42profile.authority_url))
    logger.print_info(u"\t* ignore-ssl-errors = {}".format(c42profile.ignore_ssl_errors))
    if cliprofile.get_stored_password(c42profile.name) is not None:
        logger.print_info(u"\t* A password is set.")
    logger.print_info(u"")


def create_profile(name, server, username, disable_ssl_errors=False):
    cliprofile.create_profile(name, server, username, disable_ssl_errors)
    _prompt_for_allow_password_set(name)
    get_main_cli_logger().print_info(u"Successfully created profile '{}'.".format(name))


def update_profile(name=None, server=None, username=None, disable_ssl_errors=None):
    profile = cliprofile.get_profile(name)
    cliprofile.update_profile(profile.name, server, username, disable_ssl_errors)
    _prompt_for_allow_password_set(profile.name)
    get_main_cli_logger().print_info(u"Profile '{}' has been updated.".format(profile.name))


def prompt_for_password_reset(name=None):
    """Securely prompts for your password and then stores it using keyring."""
    c42profile = cliprofile.get_profile(name)
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


def list_profiles(*args):
    """Lists all profiles that exist for this OS user."""
    profiles = cliprofile.get_all_profiles()
    logger = get_main_cli_logger()
    if not profiles:
        print_and_log_no_existing_profile()
        return
    for profile in profiles:
        logger.print_info(str(profile))


def use_profile(name):
    """Changes the default profile to the given one."""
    cliprofile.switch_default_profile(name)


def delete_profile(name):
    logger = get_main_cli_logger()
    if cliprofile.is_default_profile(name):
        logger.print_info(u"\n{} is currently the default profile!".format(name))
    if not does_user_agree(
        u"\nDeleting this profile will also delete any stored passwords and checkpoints. "
        u"Are you sure? (y/n): "
    ):
        return
    cliprofile.delete_profile(name)


def delete_all_profiles():
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


def _load_optional_profile_description(argument_collection):
    profile = argument_collection.arg_configs[u"name"]
    profile.add_short_option_name(u"-n")
    profile.set_help(PROFILE_HELP)


def _load_profile_create_descriptions(argument_collection):
    profile = argument_collection.arg_configs[u"name"]
    profile.set_help(PROFILE_HELP)
    profile.add_short_option_name(u"-n")
    argument_collection.arg_configs[u"server"].add_short_option_name(u"-s")
    argument_collection.arg_configs[u"username"].add_short_option_name(u"-u")
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
        u"For development purposes, do not validate the SSL certificates of Code42 servers. "
        u"This is not recommended unless it is required."
    )


def _prompt_for_allow_password_set(profile_name):
    if does_user_agree(u"Would you like to set a password? (y/n): "):
        prompt_for_password_reset(profile_name)
