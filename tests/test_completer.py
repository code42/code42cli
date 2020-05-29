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

