# Getting started with the code42cli

* [Licensing](#licensing)
* [Installation](#installation)
* [Authentication](#authentication)
* [Troubleshooting and Support](#troubleshooting-and-support)

## Licensing

This project uses the [MIT License](https://github.com/code42/c42sec/blob/master/LICENSE.md).

## Installation

You can install the Code42 CLI from PyPI, from source, or from distribution.

### From PyPI

The easiest and most common way is to use `pip`:

```bash
python3 -m pip install code42cli
```

To install a previous version of the Code42 CLI via `pip`, add the version number. For example, to install version
0.4.1, you would enter:

```bash
python3 -m pip install code42cli==0.5.3
```

Visit the [project history](https://pypi.org/project/code42cli/#history) on PyPI to see all published versions.

### From source

Alternatively, you can install the Code42 CLI directly from [source code](https://github.com/code42/c42sec):

```bash
git clone https://github.com/code42/c42sec.git
```

When it finishes downloading, from the root project directory, run:

```bash
python setup.py install
```

### From distribution

If you want create a `.tar` ball for installing elsewhere, run this command from the project's root directory:

```bash
python setup.py sdist
```

After it finishes building, the `.tar` ball will be located in the newly created `dist` directory. To install it, enter:

```bash
python3 -m pip install code42cli-[VERSION].tar.gz
```

## Updates

To update the CLI, use pip's `--upgrade` flag.

```bash
python3 -m pip install code42cli --upgrade
```

## Authentication

```eval_rst
.. important:: the Code42 CLI currently only supports token-based authentication.
```

To use the CLI, you must provide your credentials (basic authentication). The CLI uses keyring when storing passwords. 
If you choose not to store your password in the CLI, you have to enter it for each command that requires a connection.

The Code42 CLI currently does **not** support SSO login providers or any other identity providers such as Active 
Directory or Okta.

To learn more about authenticating in the CLI, follow the [profile guide](profile.md).

## Troubleshooting and support

### Debug mode

Debug mode may be useful if you are trying to determine if you are experiencing permissions issues. When debug mode is
on, the CLI logs HTTP request data to the console. Use the `-d` flag to enable debug mode for a particular command. 
`-d` can appear anywhere in the command chain:

```bash
code42 <command> <subcommand> <args> -d 
```

### File an issue on GitHub

If you are experiencing an issue with the Code42 CLI, you can create a *New issue* at the
[project repository](https://github.com/code42/c42sec/issues). See the Github 
[guide on creating an issue](https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue) for more information.

### Contact Code42 Support

If you don't have a GitHub account and are experiencing issues, contact
[Code42 support](https://support.code42.com/).

## What's next?

Learn how to [Set up a profile](profile.md).
