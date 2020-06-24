from os import path
from io import IOBase, StringIO

import pytest

from code42cli import PRODUCT_NAME
from code42cli.cmds.search_shared.cursor_store import Cursor, AlertCursorStore, FileEventCursorStore

PROFILE_NAME = "testprofile"
CURSOR_NAME = "testcursor"

_NAMESPACE = "{}.cmds.search_shared.cursor_store".format(PRODUCT_NAME)


@pytest.fixture
def mock_open(mocker):
    mock = mocker.patch("{}.open".format(_NAMESPACE), mocker.mock_open(read_data="TESTCHECKPOINT"))
    return mock


@pytest.fixture
def mock_remove(mocker):
    return mocker.patch("os.remove")


@pytest.fixture
def mock_listdir(mocker):
    return mocker.patch("os.listdir")


@pytest.fixture
def mock_isfile(mocker):
    mock = mocker.patch("{}.path.isfile".format(_NAMESPACE))
    mock.return_value = True
    return mock


class TestAlertCursorStore(object):
    def test_get_returns_expected_timestamp(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        checkpoint = store.get(CURSOR_NAME)
        assert checkpoint == "TESTCHECKPOINT"

    def test_get_reads_expected_file(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        store.get(CURSOR_NAME)
        user_path = path.expanduser("~/.code42cli")
        expected_path = path.join(user_path, PROFILE_NAME, "alert_checkpoints", CURSOR_NAME)
        mock_open.assert_called_once_with(expected_path)

    def test_replace_writes_to_expected_file(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.expanduser("~/.code42cli")
        expected_path = path.join(user_path, PROFILE_NAME, "alert_checkpoints", "checkpointname")
        mock_open.assert_called_once_with(expected_path, "w")

    def test_replace_writes_expected_content(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.expanduser("~/.code42cli")
        expected_path = path.join(user_path, PROFILE_NAME, "alert_checkpoints", "checkpointname")
        mock_open.return_value.write.assert_called_once_with(123)

    def test_delete_calls_remove_on_expected_file(self, mock_remove):
        store = AlertCursorStore(PROFILE_NAME)
        store.delete("deleteme")
        user_path = path.expanduser("~/.code42cli")
        expected_path = path.join(user_path, PROFILE_NAME, "alert_checkpoints", "deleteme")
        mock_remove.assert_called_once_with(expected_path)

    def test_clean_calls_remove_on_each_checkpoint(self, mock_remove, mock_listdir, mock_isfile):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = AlertCursorStore(PROFILE_NAME)
        store.clean()
        assert mock_remove.call_count == 3

    def test_get_all_cursors_returns_all_checkpoints(self, mock_listdir, mock_isfile):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = AlertCursorStore(PROFILE_NAME)
        cursors = store.get_all_cursors()
        assert len(cursors) == 3
        assert cursors[0].name == "fileone"
        assert cursors[1].name == "filetwo"
        assert cursors[2].name == "filethree"


class TestFileEventCursorStore(object):
    def test_get_returns_expected_timestamp(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        checkpoint = store.get(CURSOR_NAME)
        assert checkpoint == "TESTCHECKPOINT"

    def test_get_reads_expected_file(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        store.get(CURSOR_NAME)
        user_path = path.expanduser("~/.code42cli")
        expected_path = path.join(user_path, PROFILE_NAME, "file_event_checkpoints", CURSOR_NAME)
        mock_open.assert_called_once_with(expected_path)

    def test_replace_writes_to_expected_file(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.expanduser("~/.code42cli")
        expected_path = path.join(
            user_path, PROFILE_NAME, "file_event_checkpoints", "checkpointname"
        )
        mock_open.assert_called_once_with(expected_path, "w")

    def test_replace_writes_expected_content(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.expanduser("~/.code42cli")
        expected_path = path.join(
            user_path, PROFILE_NAME, "file_event_checkpoints", "checkpointname"
        )
        mock_open.return_value.write.assert_called_once_with(123)

    def test_delete_calls_remove_on_expected_file(self, mock_remove):
        store = FileEventCursorStore(PROFILE_NAME)
        store.delete("deleteme")
        user_path = path.expanduser("~/.code42cli")
        expected_path = path.join(user_path, PROFILE_NAME, "file_event_checkpoints", "deleteme")
        mock_remove.assert_called_once_with(expected_path)

    def test_clean_calls_remove_on_each_checkpoint(self, mock_remove, mock_listdir, mock_isfile):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = FileEventCursorStore(PROFILE_NAME)
        store.clean()
        assert mock_remove.call_count == 3

    def test_get_all_cursors_returns_all_checkpoints(self, mock_listdir, mock_isfile):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = FileEventCursorStore(PROFILE_NAME)
        cursors = store.get_all_cursors()
        assert len(cursors) == 3
        assert cursors[0].name == "fileone"
        assert cursors[1].name == "filetwo"
        assert cursors[2].name == "filethree"
