from code42cli.click_ext.groups import ExtensionGroup
from code42cli.main import CONTEXT_SETTINGS
from code42cli.options import sdk_options  # alias for convenience in extension scripts

script = ExtensionGroup(
    context_settings=CONTEXT_SETTINGS, invoke_without_command=True, no_args_is_help=True
)
