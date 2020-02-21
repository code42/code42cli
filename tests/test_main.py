import pytest

from c42sec.main import main


@pytest.fixture
def profile(mocker):
    return mocker.patch("c42sec.subcommands.profile.init")


@pytest.fixture
def checkpoint_clearer(mocker):
    return mocker.patch("c42sec.subcommands.clear_checkpoint.init")


@pytest.fixture
def printer(mocker):
    return mocker.patch("c42sec.subcommands.print_out.init")


@pytest.fixture
def writer(mocker):
    return mocker.patch("c42sec.subcommands.write_to.init")


@pytest.fixture
def sender(mocker):
    return mocker.patch("c42sec.subcommands.send_to.init")


@pytest.fixture
def arg_parser(mocker):
    return mocker.patch("argparse.ArgumentParser.parse_args")


def test_main_inits_profile(profile, arg_parser):
    main()
    assert profile.call_count == 1


def test_main_inits_clear_cursor(checkpoint_clearer, arg_parser):
    main()
    assert checkpoint_clearer.call_count == 1


def test_main_inits_print(printer, arg_parser):
    main()
    assert printer.call_count == 1


def test_main_inits_write_to(writer, arg_parser):
    main()
    assert writer.call_count == 1


def test_main_inits_send_to(sender, arg_parser):
    main()
    assert sender.call_count == 1


def test_main_calls_subcommand_with_parsed_args(mocker, arg_parser, namespace):
    arg_parser.return_value = namespace
    namespace.format = "TEST"
    namespace.exposure_types = ["EXPOSURE"]
    namespace.func = mocker.MagicMock()
    main()
    actual_args = namespace.func.call_args[0][0]
    assert actual_args == namespace
