from os import path
from io import IOBase

import pytest

from code42cli import PRODUCT_NAME
from code42cli.cmds.search_shared.cursor_store import Cursor, AlertCursorStore, FileEventCursorStore

PROFILE_NAME = "testprofile"
CURSOR_NAME = "testcursor"

_NAMESPACE = "{}.cmds.search_shared.cursor_store".format(PRODUCT_NAME)


@pytest.fixture
def mock_open(mocker):
    mock = mocker.patch("{}.open".format(_NAMESPACE))
    mock.return_value = mocker.MagicMock(spec=IOBase)
    return mock


class TestAlertCursorStore(object):
    def test_get_returns_expected_timestamp(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        store.get(CURSOR_NAME)

    def test_replace_writes_to_expected_file(self, mock_open):
        store = AlertCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)

    def test_clean_calls_remove_on_each_checkpoint(self):
        store = AlertCursorStore(PROFILE_NAME)
        store.clean()

    def test_delete_calls_remove_on_expected_file(self):
        store = AlertCursorStore(PROFILE_NAME)

    def test_get_all_cursors_returns_all_checkpoints(self):
        store = AlertCursorStore(PROFILE_NAME)


class TestFileEventCursorStore(object):
    def test_get_returns_expected_timestamp(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        store.get(CURSOR_NAME)

    def test_replace_writes_to_expected_file(self, mock_open):
        store = FileEventCursorStore(PROFILE_NAME)
        store.replace("checkpointname", 123)

    def test_clean_calls_remove_on_each_checkpoint(self):
        store = FileEventCursorStore(PROFILE_NAME)
        store.clean()

    def test_delete_calls_remove_on_expected_file(self):
        store = FileEventCursorStore(PROFILE_NAME)

    def test_get_all_cursors_returns_all_checkpoints(self):
        store = FileEventCursorStore(PROFILE_NAME)
