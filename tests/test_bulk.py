from collections import OrderedDict
from io import IOBase
import pytest
import logging
from time import sleep

from code42cli import PRODUCT_NAME
from code42cli import errors as errors
from code42cli.bulk import generate_template, BulkProcessor, run_bulk_process
from code42cli.logger import get_view_exceptions_location_message
from code42cli.progress_bar import ProgressBar

from .conftest import ErrorTrackerTestHelper, create_mock_reader


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


@pytest.fixture
def progress_bar(mocker):
    return mocker.MagicMock(spec=ProgressBar)


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
    run_bulk_process(func_with_one_arg, None)
    assert bulk_processor.run.call_count


def test_run_bulk_process_creates_processor(bulk_processor_factory):
    errors.ERRORED = False
    reader = create_mock_reader([1, 2])
    run_bulk_process(func_with_one_arg, reader)
    bulk_processor_factory.assert_called_once_with(func_with_one_arg, reader)


class TestBulkProcessor(object):
    def test_run_when_reader_returns_ordered_dict_process_kwargs(self, mock_open, progress_bar):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        reader = create_mock_reader(
            [
                OrderedDict({"test1": 1, "test2": 2}),
                OrderedDict({"test1": 3, "test2": 4}),
                OrderedDict({"test1": 5, "test2": 6}),
            ]
        )
        processor = BulkProcessor(func_for_bulk, reader, progress_bar=progress_bar)
        processor.run()
        assert (1, 2) in processed_rows
        assert (3, 4) in processed_rows
        assert (5, 6) in processed_rows

    def test_run_when_reader_returns_dict_process_kwargs(self, mock_open, progress_bar):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        reader = create_mock_reader(
            [{"test1": 1, "test2": 2}, {"test1": 3, "test2": 4}, {"test1": 5, "test2": 6}]
        )
        processor = BulkProcessor(func_for_bulk, reader, progress_bar=progress_bar)
        processor.run()
        assert (1, 2) in processed_rows
        assert (3, 4) in processed_rows
        assert (5, 6) in processed_rows

    def test_run_when_dict_reader_has_none_for_key_ignores_key(self, mock_open, progress_bar):
        processed_rows = []

        def func_for_bulk(test1):
            processed_rows.append(test1)

        reader = create_mock_reader([{"test1": 1, None: 2}])
        processor = BulkProcessor(func_for_bulk, reader, progress_bar=progress_bar)
        processor.run()
        assert processed_rows == [1]

    def test_run_when_reader_returns_strs_processes_strs(self, mock_open, progress_bar):
        processed_rows = []

        def func_for_bulk(test):
            processed_rows.append(test)

        reader = create_mock_reader(["row1", "row2", "row3"])
        processor = BulkProcessor(func_for_bulk, reader, progress_bar=progress_bar)
        processor.run()
        assert "row1" in processed_rows
        assert "row2" in processed_rows
        assert "row3" in processed_rows

    def test_run_when_error_occurs_prints_error_messages(self, mock_open, caplog):
        caplog.set_level(logging.INFO)

        def func_for_bulk(test):
            if test == "row2":
                raise Exception()

        reader = create_mock_reader(["row1", "row2", "row3"])
        with ErrorTrackerTestHelper():
            processor = BulkProcessor(func_for_bulk, reader)
            processor.run()

            with caplog.at_level(logging.ERROR):
                assert get_view_exceptions_location_message() in caplog.text

    def test_run_when_no_errors_occur_prints_success_messages(self, mock_open, caplog):
        def func_for_bulk(test):
            pass

        reader = create_mock_reader(["row1", "row2", "row3"])
        processor = BulkProcessor(func_for_bulk, reader)
        processor.run()
        with caplog.at_level(logging.INFO):
            assert "3 succeeded, 0 failed out of 3" in caplog.text

    def test_run_when_no_errors_occur_does_not_print_error_message(
        self, mock_open, caplog, progress_bar
    ):
        def func_for_bulk(test):
            pass

        reader = create_mock_reader(["row1", "row2", "row3"])
        processor = BulkProcessor(func_for_bulk, reader, progress_bar=progress_bar)

        with caplog.at_level(logging.ERROR):
            processor.run()
            assert get_view_exceptions_location_message() not in caplog.text

    def test_run_when_row_is_endline_does_not_process_row(self, mock_open, progress_bar):
        processed_rows = []

        def func_for_bulk(test):
            processed_rows.append(test)

        reader = create_mock_reader(["row1", "row2", "\n"])
        processor = BulkProcessor(func_for_bulk, reader, progress_bar=progress_bar)
        processor.run()

        assert "row1" in processed_rows
        assert "row2" in processed_rows
        assert "row3" not in processed_rows

    def test_run_when_reader_returns_dict_rows_containing_empty_strs_converts_them_to_none(
        self, mock_open, progress_bar
    ):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        reader = create_mock_reader([{"test1": "", "test2": "foo"}, {"test1": "bar", "test2": u""}])
        processor = BulkProcessor(func_for_bulk, reader, progress_bar=progress_bar)
        processor.run()
        assert (None, "foo") in processed_rows
        assert ("bar", None) in processed_rows

    @pytest.skip
    def test_run_updates_progress_bar_once_per_row(self, mock_open, progress_bar):
        def func_for_bulk(*args, **kwargs):
            pass

        rows = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        reader = create_mock_reader(rows)
        processor = BulkProcessor(func_for_bulk, reader, progress_bar=progress_bar)
        processor.run()
        assert progress_bar.update.call_count == len(rows)
