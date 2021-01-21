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
