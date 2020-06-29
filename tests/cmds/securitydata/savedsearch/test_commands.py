import pytest
from code42cli.cmds.securitydata.savedsearch.commands import SavedSearchSubCommandLoader


class TestSavedSearchSubCommandLoader(object):
    def test_load_commands_loads_expected_commands(self):
        loader = SavedSearchSubCommandLoader("Test")
        commands = loader.load_commands()
        names = [command.name for command in commands]
        assert set(names).issubset(
            [SavedSearchSubCommandLoader.LIST, SavedSearchSubCommandLoader.SHOW,]
        )
