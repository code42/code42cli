import pytest
from io import IOBase

from code42cli import PRODUCT_NAME
from code42cli.bulk import generate_template, BulkProcessor, run_bulk_process, CSVReader


_NAMESPACE = "{}.bulk".format(PRODUCT_NAME)


@pytest.fixture
def mock_open(mocker):
    mock = mocker.patch("{}.open".format(_NAMESPACE))
    mock.return_value = mocker.MagicMock(spec=IOBase)
    return mock


@pytest.fixture
def bulk_processor(mocker):
    return mocker.MagicMock(spec=BulkProcessor)


@pytest.fixture
def bulk_processor_factory(mocker, bulk_processor):
    mock_factory = mocker.patch("{}._create_bulk_processor".format(_NAMESPACE))
    mock_factory.return_value = bulk_processor
    return mock_factory


def func_for_bulk(sdk, profile, test1, test2):
    pass


def test_generate_template_uses_expected_path_and_column_names(mocker, mock_open):
    file_path = "some/path"
    template_file = mock_open.return_value.__enter__.return_value

    generate_template(func_for_bulk, file_path)
    mock_open.assert_called_once_with(file_path, u"w", encoding=u"utf8")
    template_file.write.assert_called_once_with("test1,test2")


def test_generate_template_when_given_non_callable_handler_does_not_create(mock_open):
    generate_template(None, "some/path")
    assert not mock_open.call_count


def test_run_bulk_process_calls_run(bulk_processor, bulk_processor_factory):
    run_bulk_process("some/path", func_for_bulk, None)
    assert bulk_processor.run.call_count


def test_run_bulk_process_creates_processor(bulk_processor_factory):
    reader = CSVReader()
    run_bulk_process("some/path", func_for_bulk, reader)
    bulk_processor_factory.assert_called_once_with("some/path", func_for_bulk, reader)


def test_run_bulk_process_when_not_given_reader_uses_csv_reader(bulk_processor_factory):
    run_bulk_process("some/path", func_for_bulk)
    assert type(bulk_processor_factory.call_args[0][2]) == CSVReader


class TestBulkProcessor(object):
    def test_run_when_reader_returns_dict_process_kwargs(self, mock_open):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        class MockDictReader(object):
            def __call__(self, *args, **kwargs):
                return [
                    {"test1": 1, "test2": 2},
                    {"test1": 3, "test2": 4},
                    {"test1": 5, "test2": 6},
                ]

        processor = BulkProcessor("some/path", func_for_bulk, MockDictReader())
        processor.run()
        assert processed_rows == [(1, 2), (3, 4), (5, 6)]

    def test_run_when_reader_returns_strs_processes_args(self, mock_open):
        processed_rows = []

        def func_for_bulk(test):
            processed_rows.append(test)

        class MockRowReader(object):
            def __call__(self, *args, **kwargs):
                return ["row1", "row2", "row3"]

        processor = BulkProcessor("some/path", func_for_bulk, MockRowReader())
        processor.run()
        assert processed_rows == ["row1", "row2", "row3"]
