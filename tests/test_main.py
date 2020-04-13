# run the help commands on some stuff to prove stuff loads
from code42cli.main import main


def test_securitydata_commands_load(capsys, mocker):
    mocker.patch("sys.argv", ["code42", "security-data", "print", "-h"])
    success = False
    try:
        main()
    except SystemExit:
        success = True
        capture = capsys.readouterr()
        assert "print" in capture.out
    assert success


def test_profile_commands_load(capsys, mocker):
    mocker.patch("sys.argv", ["code42", "profile", "show", "-h"])
    success = False
    try:
        main()
    except SystemExit:
        success = True
        capture = capsys.readouterr()
        assert "show" in capture.out
    assert success
