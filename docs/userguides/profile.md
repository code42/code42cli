# Configure profile

Use the [code42 profile](../commands/profile.md) set of commands to establish the Code42 environment you're working 
within and your user information. 

code42 profile
Command	Description

First, create your profile:
```bash
code42 profile create MY_FIRST_PROFILE https://example.authority.com security.admin@example.com
```

Your profile contains the necessary properties for logging into Code42 servers.
After running `code42 profile create`, the program prompts you about storing a password.
If you agree, you are then prompted to input your password.

Your password is not shown when you do `code42 profile show`.
However, `code42 profile show` will confirm that a password exists for your profile.
If you do not set a password, you will be securely prompted to enter a password each time you run a command.

For development purposes, you may need to ignore ssl errors. If you need to do this, use the `--disable-ssl-errors` option when creating your profile:

```bash
code42 profile create MY_FIRST_PROFILE https://example.authority.com security.admin@example.com --disable-ssl-errors
```

You can add multiple profiles with different names and the change the default profile with the `use` command:

```bash
code42 profile use MY_SECOND_PROFILE
```

When the `--profile` flag is available on other commands, such as those in `security-data`, it will use that profile instead of the default one.

To see all your profiles, do:

```bash
code42 profile list
```
