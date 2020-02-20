from __future__ import with_statement
import pytest

import c42sec._internal.profile.config as config


class SharedConfigMocks(object):
    mocker = None
    open_function = None
    path_exists_function = None
    get_project_path_function = None
    config_parser = None

    def setup_as_existent_profile(self):
        self.config_parser.item_getter.return_value = self._create_config_profile(is_set=True)

    def setup_as_non_existent_profile(self):
        self.config_parser.item_getter.return_value = self._create_config_profile(is_set=False)

    def _create_config_profile(self, is_set):
        config_profile = self.mocker.MagicMock()
        config_profile.getboolean.return_value = is_set
        bool_getter = self.mocker.MagicMock()
        bool_getter.return_value = is_set
        config_profile.getboolean = bool_getter
        config_profile.__setitem__ = self.mocker.MagicMock()
        return config_profile


@pytest.fixture
def shared_config_mocks(mocker, config_parser):
    # Project path
    get_project_path_function = mocker.patch("c42sec.util.get_user_project_path")
    get_project_path_function.return_value = "some/path/"

    # Opening files
    open_file_function = mocker.patch("c42sec.util.open_file")
    new_file = mocker.MagicMock()
    open_file_function.return_value = new_file

    # Path exists
    path_exists_function = mocker.patch("os.path.exists")

    mocks = SharedConfigMocks()
    mocks.mocker = mocker
    mocks.open_function = open_file_function
    mocks.path_exists_function = path_exists_function
    mocks.get_project_path_function = get_project_path_function
    mocks.config_parser = config_parser
    return mocks


def assert_save_was_called(open_file_function):
    call_args = open_file_function.call_args
    assert call_args[0][0] == "some/path/config.cfg" and call_args[0][1] == "w+"


def test_get_config_profile_when_file_exists_but_profile_does_not_exist_exits(shared_config_mocks):
    # File does indeed exist:
    shared_config_mocks.path_exists_function.return_value = True

    # Profile is not yet set:
    shared_config_mocks.setup_as_non_existent_profile()

    # It is expected to exit because the user must set their profile before they can see it.
    with pytest.raises(SystemExit):
        config.get_config_profile()


def test_get_config_profile_when_file_exists_and_profile_is_set_does_not_exit(shared_config_mocks):
    # File does indeed exist:
    shared_config_mocks.path_exists_function.return_value = True

    # Profile is indeed set:
    shared_config_mocks.setup_as_existent_profile()

    # Presumably, it shows the profile instead of exiting.
    assert config.get_config_profile()


def test_get_config_profile_when_file_does_not_exist_saves_changes(shared_config_mocks):
    # File does indeed exist:
    shared_config_mocks.path_exists_function.return_value = False

    # Profile is not yet set:
    shared_config_mocks.setup_as_non_existent_profile()

    with pytest.raises(SystemExit):
        config.get_config_profile()

    # It saves because it is writing default values to the config file
    assert_save_was_called(shared_config_mocks.open_function)


def test_mark_as_set_saves_changes(shared_config_mocks):
    shared_config_mocks.setup_as_existent_profile()
    config.mark_as_set()
    assert_save_was_called(shared_config_mocks.open_function)


def test_profile_has_been_set_when_is_set_returns_true(shared_config_mocks):
    shared_config_mocks.setup_as_existent_profile()
    assert config.profile_has_been_set()


def test_profile_has_been_set_when_is_not_set_returns_false(shared_config_mocks):
    shared_config_mocks.setup_as_non_existent_profile()
    assert not config.profile_has_been_set()


def test_set_username_saves(shared_config_mocks):
    config.set_username("New user")
    assert_save_was_called(shared_config_mocks.open_function)


def test_set_authority_url_saves(shared_config_mocks):
    config.set_authority_url("new url")
    assert_save_was_called(shared_config_mocks.open_function)


def test_set_ignore_ssl_errors_saves(shared_config_mocks):
    config.set_ignore_ssl_errors(True)
    assert_save_was_called(shared_config_mocks.open_function)
