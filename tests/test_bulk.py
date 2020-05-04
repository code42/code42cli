from collections import OrderedDict
from io import IOBase
import pytest
import logging

from code42cli import PRODUCT_NAME
from code42cli import errors as errors
from code42cli.bulk import generate_template, BulkProcessor, run_bulk_process, CSVReader
from code42cli.logger import get_view_exceptions_location_message

from .conftest import ErrorTrackerTestHelper


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


def func_with_multiple_args(sdk, profile, test1, test2):
    pass


def func_with_one_arg(sdk, profile, test1):
    pass


def test_generate_template_uses_expected_path_and_column_names(mock_open):
    file_path = "some/path"
    template_file = mock_open.return_value.__enter__.return_value

    generate_template(func_with_multiple_args, file_path)
    mock_open.assert_called_once_with(file_path, u"w", encoding=u"utf8")
    template_file.write.assert_called_once_with("test1,test2")


def test_generate_template_when_handler_has_one_arg_creates_file_without_columns(mock_open):
    file_path = "some/path"
    template_file = mock_open.return_value.__enter__.return_value

    generate_template(func_with_one_arg, "some/path")
    mock_open.assert_called_once_with(file_path, u"w", encoding=u"utf8")
    assert not template_file.write.call_count


def test_generate_template_when_handler_has_one_arg_prints_message(mock_open, caplog):
    with caplog.at_level(logging.INFO):
        generate_template(func_with_one_arg, "some/path")
        assert (
            u"A blank file was generated because there are no csv headers needed for this command. "
            u"Simply enter one test1 per line." in caplog.text
        )


def test_generate_template_when_handler_has_more_than_one_arg_does_not_print_message(
    mock_open, capsys
):
    generate_template(func_with_multiple_args, "some/path")
    capture = capsys.readouterr()
    assert (
        u"A blank file was generated because there are no csv headers needed for this command type."
        not in capture.out
    )


def test_run_bulk_process_calls_run(bulk_processor, bulk_processor_factory):
    errors.ERRORED = False
    run_bulk_process("some/path", func_with_one_arg, None)
    assert bulk_processor.run.call_count


def test_run_bulk_process_creates_processor(bulk_processor_factory):
    errors.ERRORED = False
    reader = CSVReader()
    run_bulk_process("some/path", func_with_one_arg, reader)
    bulk_processor_factory.assert_called_once_with("some/path", func_with_one_arg, reader)


def test_run_bulk_process_when_not_given_reader_uses_csv_reader(bulk_processor_factory):
    errors.ERRORED = False
    run_bulk_process("some/path", func_with_one_arg)
    assert type(bulk_processor_factory.call_args[0][2]) == CSVReader


class TestBulkProcessor(object):
    def test_run_when_reader_returns_ordered_dict_process_kwargs(self, mock_open):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        class MockDictReader(object):
            def __call__(self, *args, **kwargs):
                return [
                    OrderedDict({"test1": 1, "test2": 2}),
                    OrderedDict({"test1": 3, "test2": 4}),
                    OrderedDict({"test1": 5, "test2": 6}),
                ]

        processor = BulkProcessor("some/path", func_for_bulk, MockDictReader())
        processor.run()
        assert (1, 2) in processed_rows
        assert (3, 4) in processed_rows
        assert (5, 6) in processed_rows

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
        assert (1, 2) in processed_rows
        assert (3, 4) in processed_rows
        assert (5, 6) in processed_rows

    def test_run_when_dict_reader_has_none_for_key_ignores_key(self, mock_open):
        processed_rows = []

        def func_for_bulk(test1):
            processed_rows.append(test1)

        class MockDictReader(object):
            def __call__(self, *args, **kwargs):
                return [{"test1": 1, None: 2}]

        processor = BulkProcessor("some/path", func_for_bulk, MockDictReader())
        processor.run()
        assert processed_rows == [1]

    def test_run_when_reader_returns_strs_processes_strs(self, mock_open):
        processed_rows = []

        def func_for_bulk(test):
            processed_rows.append(test)

        class MockRowReader(object):
            def __call__(self, *args, **kwargs):
                return ["row1", "row2", "row3"]

        processor = BulkProcessor("some/path", func_for_bulk, MockRowReader())
        processor.run()
        assert "row1" in processed_rows
        assert "row2" in processed_rows
        assert "row3" in processed_rows

    def test_run_when_error_occurs_prints_error_messages(self, mock_open, caplog):
        caplog.set_level(logging.INFO)

        def func_for_bulk(test):
            if test == "row2":
                raise Exception()

        class MockRowReader(object):
            def __call__(self, *args, **kwargs):
                return ["row1", "row2", "row3"]

        with ErrorTrackerTestHelper():
            processor = BulkProcessor("some/path", func_for_bulk, MockRowReader())
            processor.run()

            with caplog.at_level(logging.INFO):
                assert "2 processed successfully out of 3." in caplog.text

            with caplog.at_level(logging.ERROR):
                assert get_view_exceptions_location_message() in caplog.text

    def test_run_when_no_errors_occur_prints_success_messages(self, mock_open, caplog):
        caplog.clear()

        def func_for_bulk(test):
            pass

        class MockRowReader(object):
            def __call__(self, *args, **kwargs):
                return ["row1", "row2", "row3"]

        processor = BulkProcessor("some/path", func_for_bulk, MockRowReader())

        with caplog.at_level(logging.INFO):
            processor.run()
            assert "3 processed successfully out of 3." in caplog.text

    def test_run_when_no_errors_occur_does_not_print_error_message(self, mock_open, caplog):
        caplog.clear()

        def func_for_bulk(test):
            pass

        class MockRowReader(object):
            def __call__(self, *args, **kwargs):
                return ["row1", "row2", "row3"]

        processor = BulkProcessor("some/path", func_for_bulk, MockRowReader())

        with caplog.at_level(logging.ERROR):
            processor.run()
            assert get_view_exceptions_location_message() not in caplog.text

    def test_run_when_row_is_endline_does_not_process_row(self, mock_open, caplog):
        caplog.clear()

        processed_rows = []

        def func_for_bulk(test):
            processed_rows.append(test)

        class MockRowReader(object):
            def __call__(self, *args, **kwargs):
                return ["row1", "row2", "\n"]

        processor = BulkProcessor("some/path", func_for_bulk, MockRowReader())
        with caplog.at_level(logging.INFO):
            processor.run()

        assert "row1" in processed_rows
        assert "row2" in processed_rows
        assert "row3" not in processed_rows
