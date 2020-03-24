# run the help commands on some stuff to prove stuff loads
import pytest

from code42cli.main import main


def test_securitydata_commands_load(capsys, mocker):
    mocker.patch("sys.argv", ["code42", "securitydata", "print", "-h"])
    with pytest.raises(SystemExit):
        main()
        capture = capsys.readouterr()
        assert "print" in capture.out


def test_profile_commands_load(capsys, mocker):
    mocker.patch("sys.argv", ["code42", "profile", "show", "-h"])
    with pytest.raises(SystemExit):
        main()
        assert "show" in capture.out
