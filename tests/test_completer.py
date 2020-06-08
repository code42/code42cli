from code42cli.completer import Completer
from code42cli.main import MainSubcommandLoader


class TestCompleter(object):
    _completer = Completer()

    def test_complete_main_returns_empty_list(self):
        actual = self._completer.complete("code4")
        assert [] == actual

    def test_complete_for_profile(self):
        actual = self._completer.complete("code42 profi")
        assert "profile" in actual

    def test_complete_for_security_data(self):
        actual = self._completer.complete("code42 security")
        assert "security-data" in actual
        assert len(actual) == 1

    def test_complete_for_alert_and_rules(self):
        actual = self._completer.complete("code42 al")
        assert "alerts" in actual
        assert "alert-rules" in actual
        assert len(actual) == 2

    def test_complete_for_departing_employee(self):
        actual = self._completer.complete("code42 de")
        assert "departing-employee" in actual
        assert len(actual) == 1

    def test_complete_for_high_risk_employee(self):
        actual = self._completer.complete("code42 hi")
        assert "high-risk-employee" in actual
        assert len(actual) == 1

    def test_profile_create(self):
        actual = self._completer.complete("code42 profile cre")
        assert "create" in actual
        assert len(actual) == 1

    def test_complete_for_high_risk_employee_bulk(self):
        actual = self._completer.complete("code42 high-risk-employee bu")
        assert "bulk" in actual
        assert len(actual) == 1

    def test_complete_for_departing_employee_bulk(self):
        actual = self._completer.complete("code42 departing-employee bu")
        assert "bulk" in actual
        assert len(actual) == 1

    def test_complete_for_alert_rules_bulk(self):
        actual = self._completer.complete("code42 alert-rules b")
        assert "bulk" in actual
        assert len(actual) == 1

    def test_complete_for_high_risk_employee_bulk_gen_template(self):
        actual = self._completer.complete("code42 high-risk-employee bulk gen")
        assert "generate-template" in actual
        assert len(actual) == 1

    def test_complete_for_departing_employee_bulk_gen_template(self):
        actual = self._completer.complete("code42 departing-employee bulk generate-")
        assert "generate-template" in actual
        assert len(actual) == 1

    def test_complete_for_alert_rules_bulk_gen_template(self):
        actual = self._completer.complete("code42 alert-rules bulk gen")
        assert "generate-template" in actual
        assert len(actual) == 1

    def test_complete_when_arg_is_first_and_complete_returns_first_set_of_options(self):
        actual = self._completer.complete("code42 ")
        assert "profile" in actual
        assert "alerts" in actual
        assert "alert-rules" in actual
        assert "security-data" in actual
        assert "departing-employee" in actual
        assert "high-risk-employee" in actual

    def test_complete_when_arg_is_complete_returns_next_options(self):
        actual = self._completer.complete("code42 departing-employee bulk")
        assert "generate-template" in actual
        assert "add" in actual
        assert "remove" in actual

    def test_complete_when_arg_is_complete_and_ends_in_space_returns_next_options(self):
        actual = self._completer.complete("code42 departing-employee bulk ")
        assert "generate-template" in actual
        assert "add" in actual
        assert "remove" in actual

    def test_complete_when_error_occurs_returns_empty_list(self, mocker):
        loader = mocker.MagicMock(spec=MainSubcommandLoader)
        completer = Completer(loader)
        actual = completer.complete("code42 dep")
        assert not actual

    def test_complete_when_completing_arg_works(self):
        actual = self._completer.complete("code42 security-data print --incre")
        assert "--incremental" in actual

    def test_complete_does_not_complete_positional_args(self):
        actual = self._completer.complete("code42 profile use nam")
        assert "name" not in actual

    def test_complete_completes_choices(self):
        actual = self._completer.complete("code42 security-data send-to 127.0.0.1 -p U")
        assert "UDP" in actual

    def test_complete_when_names_contains_filename_and_current_is_positional_completes_with_local_filenames(
        self, mocker
    ):
        mock_files = mocker.patch("code42cli.completer.get_local_files")
        mock_files.return_value = ["foo.txt", "bar.csv"]
        actual = self._completer.complete("code42 security-data write-to ")
        assert "foo.txt" in actual
        assert "bar.csv" in actual

    def test_complete_when_names_contains_file_name_and_current_is_positional_completes_with_local_filenames(
        self, mocker
    ):
        mock_files = mocker.patch("code42cli.completer.get_local_files")
        mock_files.return_value = ["foo.txt", "bar.csv"]
        actual = self._completer.complete("code42 alert-rules bulk add ")
        assert "foo.txt" in actual
        assert "bar.csv" in actual

    def test_complete_completes_local_files(self, mocker):
        mock_files = mocker.patch("code42cli.completer.get_local_files")
        mock_files.return_value = ["foo.txt", "bar.csv"]
        actual = self._completer.complete("code42 security-data write-to foo.t")
        assert "foo.txt" in actual
        assert len(actual) == 1

    def test_complete_when_current_is_prefix_to_local_file_but_is_not_arg_does_not_complete_with_local_file(
        self, mocker
    ):
        mock_files = mocker.patch("code42cli.completer.get_local_files")
        mock_files.return_value = ["bulk.txt"]
        actual = self._completer.complete("code42 departing-employee bu")
        assert "bulk.txt" not in actual
        assert "bulk" in actual

    def test_complete_when_nothing_matches_top_level_command_returns_nothing(self):
        actual = self._completer.complete("code42 XX")
        assert not actual

    def test_complete_when_nothing_matches_second_level_commands_returns_nothing(self):
        actual = self._completer.complete("code42 security-data prX")
        assert not actual

    def test_complete_when_nothing_matches_flagged_arg_returns_nothing(self):
        actual = self._completer.complete("code42 security-data print --begX")
        assert not actual

    def test_complete_when_nothing_matches_choice_returns_nothing(self):
        actual = self._completer.complete("code42 security-data send-to -p XX")
        assert not actual

    def test_complete_when_nothing_matches_files_return_nothing(self, mocker):
        mock_files = mocker.patch("code42cli.completer.get_local_files")
        mock_files.return_value = ["bulk.txt"]
        actual = self._completer.complete("code42 departing-employee buX")
        assert not actual
