import pytest

import c42sec.profile._config as config


@pytest.fixture
def path_exists_function(mocker):
    return mocker.patch("os.path.exists")


@pytest.fixture
def path_exists(path_exists_function):
    path_exists_function.return_value = True
    return path_exists_function


@pytest.fixture
def path_does_not_exist(path_exists_function):
    path_exists_function.return_value = False
    return path_exists_function


@pytest.fixture
def config_section_getter(mocker):
    return mocker.patch("configparser.ConfigParser.__getitem__")


@pytest.fixture
def non_existent_profile(mocker, config_section_getter, config_parser):
    config_section_getter.return_value = create_config_profile(mocker, False)


@pytest.fixture
def existent_profile(mocker, config_section_getter, config_parser):
    config_section_getter.return_value = create_config_profile(mocker, True)


@pytest.fixture
def mock_project_path(mocker):
    project_path_getter = mocker.patch("c42sec.util.get_user_project_path")
    project_path_getter.return_value = "some/path"
    return project_path_getter


@pytest.fixture
def open_file_function(mocker):
    open_file = mocker.patch("c42sec.util.open_file")
    new_file = mocker.MagicMock()
    open_file.return_value = new_file
    return open_file


def create_config_profile(mocker, is_set):
    config_profile = mocker.MagicMock()
    bool_getter = mocker.MagicMock()
    bool_getter.return_value = is_set
    config_profile.getboolean = bool_getter
    return config_profile


def assert_save_was_called(open_file_function):
    call_args = open_file_function.call_args
    assert call_args[0][0] == "some/pathconfig.cfg" and call_args[0][1] == "w+"


def test_get_config_profile_when_file_exists_but_profile_not_set_exits(
    path_exists, non_existent_profile, mock_project_path
):
    with pytest.raises(SystemExit):
        config.get_config_profile()


def test_get_config_profile_when_file_exists_but_profile_is_set_does_not_exit(
    path_exists, existent_profile, mock_project_path
):
    assert config.get_config_profile()


def test_get_config_profile_when_path_does_not_exist_saves_changes(
    path_does_not_exist, open_file_function, mock_project_path, non_existent_profile
):
    with pytest.raises(SystemExit):
        config.get_config_profile()

    assert_save_was_called(open_file_function)


def test_mark_as_set_saves_changes(existent_profile, open_file_function, mock_project_path):
    config.mark_as_set()
    assert_save_was_called(open_file_function)


def test_profile_has_been_set_when_when_getboolean_returns_true_returns_true(
    existent_profile, open_file_function
):
    assert config.profile_has_been_set()


def test_profile_has_been_set_when_when_getboolean_returns_false_returns_false(
    non_existent_profile, open_file_function
):
    assert not config.profile_has_been_set()


def test_set_username_saves(
    path_does_not_exist, open_file_function, mock_project_path, existent_profile
):
    config.set_username("New user")
    assert_save_was_called(open_file_function)


def test_set_authority_url_saves(
    path_does_not_exist, open_file_function, mock_project_path, existent_profile
):
    config.set_authority_url("new url")
    assert_save_was_called(open_file_function)


def test_set_ignore_ssl_errors_saves(
    path_does_not_exist, open_file_function, mock_project_path, existent_profile
):
    config.set_ignore_ssl_errors(True)
    assert_save_was_called(open_file_function)
