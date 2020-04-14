import pytest
from io import IOBase

from code42cli import PRODUCT_NAME
from code42cli.bulk import generate_template, BulkProcessor


@pytest.fixture
def mock_open(mocker):
    mock = mocker.patch("{}.bulk.open".format(PRODUCT_NAME))
    mock.return_value = mocker.MagicMock(spec=IOBase)
    return mock


def test_generate_template_uses_expected_path_and_column_names(mocker, mock_open):
    def func_for_bulk(sdk, profile, test1, test2):
        pass

    file_path = "some/path"
    template_file = mock_open.return_value.__enter__.return_value

    generate_template(func_for_bulk, file_path)
    mock_open.assert_called_once_with(file_path, u"w", encoding=u"utf8")
    template_file.write.assert_called_once_with("test1,test2")


def test_generate_template_when_given_non_callable_handler_does_not_create(mock_open):
    generate_template(None, "some/path")
    assert not mock_open.call_count


class TestBulkProcessor(object):
    def test_run_processes_rows(self, mocker, mock_open):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        dict_reader = mocker.patch("{}.bulk._create_dict_reader".format(PRODUCT_NAME))
        dict_reader.return_value = [
            {"test1": 1, "test2": 2},
            {"test1": 3, "test2": 4},
            {"test1": 5, "test2": 6},
        ]
        processor = BulkProcessor("some/path", func_for_bulk)
        processor.run()
        assert processed_rows == [(1, 2), (3, 4), (5, 6)]
