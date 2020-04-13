from code42cli.bulk import generate_template, BulkProcessor


def test_generate_template_uses_expected_path_and_column_names(mocker):
    def func_for_bulk(sdk, profile, test1, test2):
        pass

    template_writer = mocker.patch("code42cli.bulk._write_template_file")
    generate_template(func_for_bulk, "some/path")
    template_writer.assert_called_once_with("some/path", ["test1", "test2"])


def test_generate_template_when_given_non_callable_handler_does_not_create(mocker):
    mock_open = mocker.patch("code42cli.bulk.open")
    generate_template(None, "some/path")
    assert not mock_open.call_count


class TestBulkProcessor(object):
    def test_run_processes_rows(self, mocker):
        processed_rows = []

        def func_for_bulk(test1, test2):
            processed_rows.append((test1, test2))

        mocker.patch("code42cli.bulk.open")
        dict_reader = mocker.patch("code42cli.bulk._create_dict_reader")
        dict_reader.return_value = [
            {"test1": 1, "test2": 2},
            {"test1": 3, "test2": 4},
            {"test1": 5, "test2": 6},
        ]
        processor = BulkProcessor("some/path", func_for_bulk)
        processor.run()
        assert processed_rows == [(1, 2), (3, 4), (5, 6)]
