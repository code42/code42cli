from code42cli.click_ext.groups import ExtensionGroup
from code42cli.main import CONTEXT_SETTINGS

script = ExtensionGroup(
    context_settings=CONTEXT_SETTINGS, invoke_without_command=True, no_args_is_help=True
)
