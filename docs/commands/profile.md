# Profile Commands

### show
  
Print the details of a profile. Arguments:
* `--name`, `-n` (optional): The name of the Code42 profile to use when executing this command.

Usage:
```bash
code42 profile show <optional-arguments>
```
  
### list

Show all existing stored profiles. This command takes no arguments.

Usage:
```bash
code42 profile list
```

### use

Set a profile as the default. Arguments:
* `name`: The name of the profile to set as active.

Usage:
```bash
code42 profile use <profile-name>
```
  
### reset-pw

Change the stored password for a profile. Arguments:
* `--name`, `-n` (optional): The name of the Code42 profile to use when executing this command.

Usage:
```bash
code42 profile reset-pw <optional-args>
```

### create

Create profile settings. The first profile created will be the default. Arguments:
* `--name`, `-n`: The name of the code42cli profile to use when executing this command.
* `--server`, `-s`: The url and port of the Code42 server.
* `--username`, `-u`: The username of the Code42 API user.
* `--disable-ssl-errors` (optional): For development purposes, do not validate the SSL certificates of Code42 servers. 
    This is not recommended unless it is required.

Usage:
```bash
code42 profile create --name <profile-name> --server <server> --username <username> <optional-args>
```


### update

Update an existing profile. Arguments:
* `--name`, `-n`: The name of the code42cli profile to use when executing this command.
* `--server`, `-s`: The url and port of the Code42 server.
* `--username`, `-u`: The username of the Code42 API user.
* `--disable-ssl-errors` (optional): For development purposes, do not validate the SSL certificates of Code42 servers. 
    This is not recommended unless it is required.

Usage:
```bash
code42 profile update <optional-args>
```

### delete

Deletes a profile and its stored password (if any).  Arguments:
* `name`: The name of the code42cli profile you wish to delete.

Usage:
```bash
code42 profile delete <profile-name>
```


### delete-all

Deletes all profiles and saved passwords (if any). This command has no arguments.

Usage:
```bash
code42 profile delete-all
```
