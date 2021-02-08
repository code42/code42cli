from distutils.core import setup

setup(
    name="SettingsPlugin",
    version="0.1",
    packages=["settings_plugin"],
    install_requires=["code42cli"],
    entry_points="""
        [code42cli.plugins]
        get_device_settings=settings_plugin.script:get_device_settings
        get_device_user=settings_plugin.script:get_device_user
    """,
)
