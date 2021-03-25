# Get started with the Code42 command-line interface (CLI)

* [Licensing](#licensing)
* [Installation](#installation)
* [Authentication](#authentication)
* [Troubleshooting and Support](#troubleshooting-and-support)

## Licensing

This project uses the [MIT License](https://github.com/code42/code42cli/blob/master/LICENSE.md).

## Installation

You can install the Code42 CLI from PyPI, from source, or from distribution.

### From PyPI

The easiest and most common way is to use `pip`:

```bash
python3 -m pip install code42cli
```

To install a previous version of the Code42 CLI via `pip`, add the version number. For example, to install version
0.4.1, enter:

```bash
python3 -m pip install code42cli==0.5.3
```

Visit the [project history](https://pypi.org/project/code42cli/#history) on PyPI to see all published versions.

### From source

Alternatively, you can install the Code42 CLI directly from [source code](https://github.com/code42/code42cli):

```bash
git clone https://github.com/code42/code42cli.git
```

When it finishes downloading, from the root project directory, run:

```bash
python setup.py install
```

### From distribution

If you want create a `.tar` ball for installing elsewhere, run the following command from the project's root directory:

```bash
python setup.py sdist
```

After it finishes building, the `.tar` ball will be located in the newly created `dist` directory. To install it, enter:

```bash
python3 -m pip install code42cli-[VERSION].tar.gz
```

## Updates

To update the CLI, use the pip `--upgrade` flag.

```bash
python3 -m pip install code42cli --upgrade
```

## Authentication

```eval_rst
.. important:: The Code42 CLI currently only supports token-based authentication.
```

Create a user in Code42 to authenticate (basic authentication) and access data via the CLI. The CLI returns data based on the roles assigned to this user. To ensure that the user's rights are not too permissive, create a user with the lowest level of privilege necessary. See our [Role assignment use cases](https://support.code42.com/Administrator/Cloud/Monitoring_and_managing/Role_assignment_use_cases) for information on recommended roles. We recommend you test to confirm that the user can access the right data. 

If you choose not to store your password in the CLI, you must enter it for each command that requires a connection.

The Code42 CLI currently does **not** support SSO login providers or any other identity providers such as Active
Directory or Okta.

### Windows and Mac

For Windows and Mac systems, the CLI uses Keyring when storing passwords.

### Red Hat Enterprise Linux

To use Keyring to store the credentials you enter in the Code42 CLI, enter the following commands before installing.
```bash
yum -y install python-pip python3 dbus-python gnome-keyring libsecret dbus-x11
pip3 install code42cli
```
If the following directories do not already exist, create them:
```bash
mkdir -p ~/.cache
mkdir -p ~/.local/share/keyring
```
In the following commands, replace the example value `\n` with the Keyring password (if the default Keyring already exists).
```bash
eval "$(dbus-launch --sh-syntax)"
eval "$(printf '\n' | gnome-keyring-daemon --unlock)"
eval "$(printf '\n' | /usr/bin/gnome-keyring-daemon --start)"
```
Close out your D-bus session and GNOME Keyring:
```bash
pkill gnome
pkill dbus
```
If you do not use Keyring to store your credentials, the Code42 CLI will ask permission to store your credentials in a local flat file with read/write permissions for only the operating system user who set the password. Alternatively, you can enter your password with each command you enter.

### Ubuntu
If Keyring doesn't support your Ubuntu system, the Code42 CLI will ask permission to store your credentials in a local flat file with read/write permissions for only the operating system user who set the password. Alternatively, you can enter your password with each command you enter.



To learn more about authenticating in the CLI, follow the [Configure profile guide](profile.md).

## Troubleshooting and support

### Debug mode

Debug mode may be useful if you are trying to determine if you are experiencing permissions issues. When debug mode is
on, the CLI logs HTTP request data to the console. Use the `-d` flag to enable debug mode for a particular command.
`-d` can appear anywhere in the command chain:

```bash
code42 <command> <subcommand> <args> -d
```

### File an issue on GitHub

If you are experiencing an issue with the Code42 CLI, select *New issue* at the
[project repository](https://github.com/code42/code42cli/issues) to create an issue. See the Github
[guide on creating an issue](https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue) for more information.

### Contact Code42 Support

If you don't have a GitHub account and are experiencing issues, contact
[Code42 support](https://support.code42.com/).

## What's next?

Learn how to [Set up a profile](profile.md).
