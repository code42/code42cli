import click

username_arg = click.argument("username")
cloud_alias_option = click.option(
    "--cloud-alias",
    help="If the employee has an email alias other than their Code42 username "
    "that they use for cloud services such as Google Drive, OneDrive, or Box, "
    "add and monitor the alias. WARNING: Adding a cloud alias will override any "
    "existing cloud alias for this user.",
)
notes_option = click.option("--notes", help="Optional notes about the employee.")
