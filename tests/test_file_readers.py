import pytest

from code42cli.click_ext.types import AutoDecodedFile
from code42cli.errors import Code42CLIError
from code42cli.file_readers import read_csv

HEADERLESS_CSV = [
    "col1_val1,col2_val1,col3_val1\n",
    "col1_val2,col2_val2,col3_val2\n",
]
HEADERS = ["header1", "header2", "header3"]
HEADERED_CSV = [
    "header2,header1,header3,extra_column\n"
    "col2_val1,col1_val1,col3_val1,extra_value\n",
    "col2_val2,col1_val2,col3_val2,extra_value\n",
]


def test_read_csv_handles_headerless_columns_in_proper_number_and_order(runner):
    with runner.isolated_filesystem():
        with open("test_csv.csv", "w") as csv:
            csv.writelines(HEADERLESS_CSV)
        with open("test_csv.csv") as csv:
            result_list = read_csv(file=csv, headers=HEADERS)
        assert result_list[0]["header1"] == "col1_val1"
        assert result_list[1]["header3"] == "col3_val2"


def test_read_csv_handles_headered_columns_in_arbitrary_number_and_order(runner):
    with runner.isolated_filesystem():
        with open("test_csv.csv", "w") as csv:
            csv.writelines(HEADERED_CSV)
        with open("test_csv.csv") as csv:
            result_list = read_csv(file=csv, headers=HEADERS)
        assert result_list[0]["header1"] == "col1_val1"
        assert result_list[1]["header3"] == "col3_val2"


def test_read_csv_raises_when_no_header_detected_and_column_count_doesnt_match_expected_header(
    runner,
):
    with runner.isolated_filesystem():
        with open("test_csv.csv", "w") as csv:
            csv.writelines(HEADERLESS_CSV)
        with open("test_csv.csv") as csv:
            with pytest.raises(Code42CLIError):
                read_csv(csv, ["column1", "column2"])


def test_read_csv_when_all_expected_headers_present_filters_out_extra_columns(runner):
    with runner.isolated_filesystem():
        with open("test_csv.csv", "w") as csv:
            csv.writelines(HEADERED_CSV)
        with open("test_csv.csv") as csv:
            result_list = read_csv(file=csv, headers=HEADERS)
            assert "extra_column" not in result_list[0]


def test_read_csv_when_some_but_not_all_required_headers_present_raises(runner):
    with runner.isolated_filesystem():
        with open("test_csv.csv", "w") as csv:
            csv.writelines(HEADERED_CSV)
        with open("test_csv.csv") as csv:
            with pytest.raises(Code42CLIError):
                read_csv(file=csv, headers=HEADERS + ["extra_header"])


@pytest.mark.parametrize(
    "encoding", ["utf8", "utf16", "latin_1"],
)
def test_read_csv_reads_various_encodings_automatically(runner, encoding):
    with runner.isolated_filesystem():
        with open("test.csv", "w", encoding=encoding) as file:
            file.write("".join(HEADERED_CSV))

        csv = AutoDecodedFile("r").convert("test.csv", None, None)
        result_list = read_csv(csv, headers=HEADERS)

        assert result_list == [
            {"header1": "col1_val1", "header2": "col2_val1", "header3": "col3_val1"},
            {"header1": "col1_val2", "header2": "col2_val2", "header3": "col3_val2"},
        ]
