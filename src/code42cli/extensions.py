from code42cli.click_ext.groups import ExtensionGroup
from code42cli.main import CONTEXT_SETTINGS

# alias for convenience in extension scripts
from code42cli.options import sdk_options  # noqa: F401

script = ExtensionGroup(
    context_settings=CONTEXT_SETTINGS, invoke_without_command=True, no_args_is_help=True
)
