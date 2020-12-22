from os import path

import pytest

from code42cli import PRODUCT_NAME
from code42cli.cmds.search.cursor_store import AlertCursorStore
from code42cli.cmds.search.cursor_store import AuditLogCursorStore
from code42cli.cmds.search.cursor_store import Cursor
from code42cli.cmds.search.cursor_store import FileEventCursorStore
from code42cli.errors import Code42CLIError

PROFILE_NAME = "testprofile"
CURSOR_NAME = "testcursor"

_NAMESPACE = "{}.cmds.search.cursor_store".format(PRODUCT_NAME)

ALERT_CHECKPOINT_FOLDER_NAME = "alert_checkpoints"
FILE_EVENT_CHECKPOINT_FOLDER_NAME = "file_event_checkpoints"
AUDIT_LOG_CHECKPOINT_FOLDER_NAME = "audit_log_checkpoints"


@pytest.fixture
def mock_open(mocker):
    mock = mocker.patch("builtins.open", mocker.mock_open(read_data="123456789"))
    return mock


AUDIT_LOG_EVENT_HASH_1 = "bc8f70ff821cadcc3e717d534d14737d"
AUDIT_LOG_EVENT_HASH_2 = "66ad12c0a0dba2b41520fb69aeefd84d"


@pytest.fixture
def mock_open_events(mocker):
    mock = mocker.patch(
        "builtins.open",
        mocker.mock_open(
            read_data='["{}", "{}"]'.format(
                AUDIT_LOG_EVENT_HASH_1, AUDIT_LOG_EVENT_HASH_2
            )
        ),
    )
    return mock


@pytest.fixture
def mock_isfile(mocker):
    mock = mocker.patch("{}.os.path.isfile".format(_NAMESPACE))
    mock.return_value = True
    return mock


class TestCursor:
    def test_name_returns_expected_name(self):
        cursor = Cursor("bogus/path")
        assert cursor.name == "path"

    def test_value_returns_expected_value(self, mock_open):
        cursor = Cursor("bogus/path")
        assert cursor.value == "123456789"

    def test_value_reads_expected_file(self, mock_open):
        cursor = Cursor("bogus/path")
        _ = cursor.value
        mock_open.assert_called_once_with("bogus/path")


class TestAlertCursorStore:
    def test_get_returns_expected_timestamp(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        checkpoint = store.get(CURSOR_NAME)
        assert checkpoint == 123456789

    def test_get_when_profile_does_not_exist_returns_none(self, mocker):
        store = AlertCursorStore(PROFILE_NAME)
        checkpoint = store.get(CURSOR_NAME)
        mock_open = mocker.patch("{}.open".format(_NAMESPACE))
        mock_open.side_effect = FileNotFoundError
        assert checkpoint is None

    def test_get_reads_expected_file(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        store.get(CURSOR_NAME)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, ALERT_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, CURSOR_NAME
        )
        mock_open.assert_called_once_with(expected_path)

    def test_replace_writes_to_expected_file(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, ALERT_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "checkpointname"
        )
        mock_open.assert_called_once_with(expected_path, "w")

    def test_replace_writes_expected_content(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        path.join(
            user_path, ALERT_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "checkpointname"
        )
        mock_open.return_value.write.assert_called_once_with("123")

    def test_delete_calls_remove_on_expected_file(self, mock_open, mock_remove):
        store = AlertCursorStore(PROFILE_NAME)
        store.delete("deleteme")
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, ALERT_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "deleteme"
        )
        mock_remove.assert_called_once_with(expected_path)

    def test_delete_when_checkpoint_does_not_exist_raises_cli_error(
        self, mock_open, mock_remove
    ):
        store = AlertCursorStore(PROFILE_NAME)
        mock_remove.side_effect = FileNotFoundError
        with pytest.raises(Code42CLIError):
            store.delete("deleteme")

    def test_clean_calls_remove_on_each_checkpoint(
        self, mock_open, mock_remove, mock_listdir, mock_isfile
    ):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = AlertCursorStore(PROFILE_NAME)
        store.clean()
        assert mock_remove.call_count == 3

    def test_get_all_cursors_returns_all_checkpoints(
        self, mock_open, mock_listdir, mock_isfile
    ):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = AlertCursorStore(PROFILE_NAME)
        cursors = store.get_all_cursors()
        assert len(cursors) == 3
        assert cursors[0].name == "fileone"
        assert cursors[1].name == "filetwo"
        assert cursors[2].name == "filethree"


class TestFileEventCursorStore:
    def test_get_returns_expected_timestamp(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        checkpoint = store.get(CURSOR_NAME)
        assert checkpoint == 123456789

    def test_get_reads_expected_file(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        store.get(CURSOR_NAME)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, FILE_EVENT_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, CURSOR_NAME
        )
        mock_open.assert_called_once_with(expected_path)

    def test_get_when_profile_does_not_exist_returns_none(self, mocker):
        store = FileEventCursorStore(PROFILE_NAME)
        checkpoint = store.get(CURSOR_NAME)
        mock_open = mocker.patch("{}.open".format(_NAMESPACE))
        mock_open.side_effect = FileNotFoundError
        assert checkpoint is None

    def test_replace_writes_to_expected_file(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, FILE_EVENT_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "checkpointname"
        )
        mock_open.assert_called_once_with(expected_path, "w")

    def test_replace_writes_expected_content(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        path.join(
            user_path, FILE_EVENT_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "checkpointname"
        )
        mock_open.return_value.write.assert_called_once_with("123")

    def test_delete_calls_remove_on_expected_file(self, mock_open, mock_remove):
        store = FileEventCursorStore(PROFILE_NAME)
        store.delete("deleteme")
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, FILE_EVENT_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "deleteme"
        )
        mock_remove.assert_called_once_with(expected_path)

    def test_delete_when_checkpoint_does_not_exist_raises_cli_error(
        self, mock_open, mock_remove
    ):
        store = FileEventCursorStore(PROFILE_NAME)
        mock_remove.side_effect = FileNotFoundError
        with pytest.raises(Code42CLIError):
            store.delete("deleteme")

    def test_clean_calls_remove_on_each_checkpoint(
        self, mock_open, mock_remove, mock_listdir, mock_isfile
    ):
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


class TestAuditLogCursorStore:
    def test_get_returns_expected_timestamp(self, mock_open):
        store = AuditLogCursorStore(PROFILE_NAME)
        checkpoint = store.get(CURSOR_NAME)
        assert checkpoint == 123456789

    def test_get_reads_expected_file(self, mock_open):
        store = AuditLogCursorStore(PROFILE_NAME)
        store.get(CURSOR_NAME)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, AUDIT_LOG_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, CURSOR_NAME
        )
        mock_open.assert_called_once_with(expected_path)

    def test_get_when_profile_does_not_exist_returns_none(self, mocker):
        store = AuditLogCursorStore(PROFILE_NAME)
        checkpoint = store.get(CURSOR_NAME)
        mock_open = mocker.patch("{}.open".format(_NAMESPACE))
        mock_open.side_effect = FileNotFoundError
        assert checkpoint is None

    def test_replace_writes_to_expected_file(self, mock_open):
        store = AuditLogCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, AUDIT_LOG_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "checkpointname"
        )
        mock_open.assert_called_once_with(expected_path, "w")

    def test_replace_writes_expected_content(self, mock_open):
        store = AuditLogCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        path.join(
            user_path, AUDIT_LOG_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "checkpointname"
        )
        mock_open.return_value.write.assert_called_once_with("123")

    def test_delete_calls_remove_on_expected_file(self, mock_open, mock_remove):
        store = AuditLogCursorStore(PROFILE_NAME)
        store.delete("deleteme")
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path, AUDIT_LOG_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, "deleteme"
        )
        mock_remove.assert_called_once_with(expected_path)

    def test_delete_when_checkpoint_does_not_exist_raises_cli_error(
        self, mock_open, mock_remove
    ):
        store = AuditLogCursorStore(PROFILE_NAME)
        mock_remove.side_effect = FileNotFoundError
        with pytest.raises(Code42CLIError):
            store.delete("deleteme")

    def test_clean_calls_remove_on_each_checkpoint(
        self, mock_open, mock_remove, mock_listdir, mock_isfile
    ):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = AuditLogCursorStore(PROFILE_NAME)
        store.clean()
        assert mock_remove.call_count == 3

    def test_get_all_cursors_returns_all_checkpoints(self, mock_listdir, mock_isfile):
        mock_listdir.return_value = ["fileone", "filetwo", "filethree"]
        store = AuditLogCursorStore(PROFILE_NAME)
        cursors = store.get_all_cursors()
        assert len(cursors) == 3
        assert cursors[0].name == "fileone"
        assert cursors[1].name == "filetwo"
        assert cursors[2].name == "filethree"

    def test_get_events_returns_expected_list(self, mock_open_events):
        store = AuditLogCursorStore(PROFILE_NAME)
        event_list = store.get_events(CURSOR_NAME)
        assert event_list == [AUDIT_LOG_EVENT_HASH_1, AUDIT_LOG_EVENT_HASH_2]

    def test_get_events_reads_expected_file(self, mock_open):
        store = AuditLogCursorStore(PROFILE_NAME)
        store.get_events(CURSOR_NAME)
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_filename = CURSOR_NAME + "_events"
        expected_path = path.join(
            user_path, AUDIT_LOG_CHECKPOINT_FOLDER_NAME, PROFILE_NAME, expected_filename
        )
        mock_open.assert_called_once_with(expected_path)

    def test_get_events_when_profile_does_not_exist_returns_empty_list(self, mocker):
        store = AuditLogCursorStore(PROFILE_NAME)
        event_list = store.get_events(CURSOR_NAME)
        mock_open = mocker.patch("{}.open".format(_NAMESPACE))
        mock_open.side_effect = FileNotFoundError
        assert event_list == []

    def test_get_events_when_checkpoint_not_valid_json_returns_empty_list(self, mocker):
        mocker.patch("builtins.open", mocker.mock_open(read_data="invalid_json"))
        store = AuditLogCursorStore(PROFILE_NAME)
        event_list = store.get_events(CURSOR_NAME)
        assert event_list == []

    def test_replace_events_writes_to_expected_file(self, mock_open):
        store = AuditLogCursorStore(PROFILE_NAME)
        store.replace_events("checkpointname", ["hash1", "hash2"])
        user_path = path.join(path.expanduser("~"), ".code42cli")
        expected_path = path.join(
            user_path,
            AUDIT_LOG_CHECKPOINT_FOLDER_NAME,
            PROFILE_NAME,
            "checkpointname_events",
        )
        mock_open.assert_called_once_with(expected_path, "w")

    def test_replace_events_writes_expected_content(self, mock_open_events):
        store = AuditLogCursorStore(PROFILE_NAME)
        store.replace_events("checkpointname", ["hash1", "hash2"])
        user_path = path.join(path.expanduser("~"), ".code42cli")
        path.join(
            user_path,
            AUDIT_LOG_CHECKPOINT_FOLDER_NAME,
            PROFILE_NAME,
            "checkpointname_events",
        )
        mock_open_events.return_value.write.assert_called_once_with(
            '["hash1", "hash2"]'
        )
