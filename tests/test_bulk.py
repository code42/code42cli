from collections import OrderedDict

import pytest

from code42cli import errors
from code42cli import PRODUCT_NAME
from code42cli.bulk import BulkProcessor
from code42cli.bulk import run_bulk_process
from code42cli.logging.logger import get_view_error_details_message

_NAMESPACE = "{}.bulk".format(PRODUCT_NAME)


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


def test_run_bulk_process_calls_run(bulk_processor, bulk_processor_factory):
    errors.ERRORED = False
    run_bulk_process(func_with_one_arg, None)
    assert bulk_processor.run.call_count


def test_run_bulk_process_creates_processor(bulk_processor_factory):
    errors.ERRORED = False
    rows = [1, 2]
    run_bulk_process(func_with_one_arg, rows)
    bulk_processor_factory.assert_called_once_with(func_with_one_arg, rows, None)


class TestBulkProcessor:
    def test_run_when_reader_returns_ordered_dict_process_kwargs(self):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        rows = [
            OrderedDict({"test1": 1, "test2": 2}),
            OrderedDict({"test1": 3, "test2": 4}),
            OrderedDict({"test1": 5, "test2": 6}),
        ]
        processor = BulkProcessor(func_for_bulk, rows)
        processor.run()
        assert (1, 2) in processed_rows
        assert (3, 4) in processed_rows
        assert (5, 6) in processed_rows

    def test_run_when_reader_returns_dict_process_kwargs(self):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        rows = [
            {"test1": 1, "test2": 2},
            {"test1": 3, "test2": 4},
            {"test1": 5, "test2": 6},
        ]
        processor = BulkProcessor(func_for_bulk, rows)
        processor.run()
        assert (1, 2) in processed_rows
        assert (3, 4) in processed_rows
        assert (5, 6) in processed_rows

    def test_run_when_dict_reader_has_none_for_key_ignores_key(self):
        processed_rows = []

        def func_for_bulk(test1):
            processed_rows.append(test1)

        rows = [{"test1": 1, None: 2}]
        processor = BulkProcessor(func_for_bulk, rows)
        processor.run()
        assert processed_rows == [1]

    def test_run_when_reader_returns_strs_processes_strs(self):
        processed_rows = []

        def func_for_bulk(test):
            processed_rows.append(test)

        rows = ["row1", "row2", "row3"]
        processor = BulkProcessor(func_for_bulk, rows)
        processor.run()
        assert "row1" in processed_rows
        assert "row2" in processed_rows
        assert "row3" in processed_rows

    def test_run_when_error_occurs_raises_expected_logged_cli_error(self):
        def func_for_bulk(test):
            if test == "row2":
                raise Exception()

        rows = ["row1", "row2", "row3"]
        with pytest.raises(errors.LoggedCLIError) as err:
            processor = BulkProcessor(func_for_bulk, rows)
            processor.run()

        assert err.value.message == "Some problems occurred during bulk processing."

    def test_run_when_no_errors_occur_does_not_print_error_message(self, capsys):
        def func_for_bulk(test):
            pass

        rows = ["row1", "row2", "row3"]
        processor = BulkProcessor(func_for_bulk, rows)

        processor.run()
        output = capsys.readouterr()
        assert get_view_error_details_message() not in output.out

    def test_run_when_row_is_endline_does_not_process_row(self):
        processed_rows = []

        def func_for_bulk(test):
            processed_rows.append(test)

        rows = ["row1", "row2", "\n"]
        processor = BulkProcessor(func_for_bulk, rows)
        processor.run()

        assert "row1" in processed_rows
        assert "row2" in processed_rows
        assert "row3" not in processed_rows

    def test_run_when_reader_returns_dict_rows_containing_empty_strs_converts_them_to_none(
        self,
    ):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        rows = [{"test1": "", "test2": "foo"}, {"test1": "bar", "test2": ""}]
        processor = BulkProcessor(func_for_bulk, rows)
        processor.run()
        assert (None, "foo") in processed_rows
        assert ("bar", None) in processed_rows
