# Configure profile

Use the [code42 profile](../commands/profile.md) set of commands to establish the Code42 environment you're working
within and your user information.

First, create your profile:
```bash
code42 profile create --name MY_FIRST_PROFILE --server example.authority.com --username security.admin@example.com
```

Your profile contains the necessary properties for authenticating with Code42. After running `code42 profile create`,
the program prompts you about storing a password. If you agree, you are then prompted to enter your password.

Your password is not shown when you do `code42 profile show`. However, `code42 profile show` will confirm that a
password exists for your profile. If you do not set a password, you will be securely prompted to enter a password each
time you run a command.

You can add multiple profiles with different names and the change the default profile with the `use` command:

```bash
code42 profile use MY_SECOND_PROFILE
```

When you use the `--profile` flag with other commands, such as those in `security-data`, that profile is used
instead of the default profile. For example,

```bash
code42 security-data search -b 2020-02-02 --profile MY_SECOND_PROFILE
```

To see all your profiles, do:

```bash
code42 profile list
```
