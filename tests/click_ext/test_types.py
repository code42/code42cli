from code42cli.click_ext.types import PromptChoice


class TestPromptChoice:
    def test_convert_returns_expected_item(self):
        choices = ["foo", "bar", "test"]
        prompt_choice = PromptChoice(choices)
        assert prompt_choice.convert("1", None, None) == "foo"
        assert prompt_choice.convert("2", None, None) == "bar"
        assert prompt_choice.convert("3", None, None) == "test"
